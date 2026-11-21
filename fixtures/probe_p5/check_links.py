"""Night order 1 (probe P5), step 2: ask for every source link on a card, once.

Read-only. It reads results/*.json (written by probe.py), takes the one
"Source record" link each Approved, In trials or New clues card shows, and
asks for each different link once: HEAD first, then GET if HEAD is refused.
A GET never reads the page: the connection is closed after the status line.

Polite: one request at a time, and at least GAP seconds between two
requests to the same host. If a host says "slow down" (429 or 503) the
script waits, doubles that host's gap and tries the link again, at most
TRIES times. If a host refuses REFUSALS_TO_STOP links in a row it is left
alone, and its remaining links are written down as not asked.

Redirects are followed by hand, one hop at a time, so every hop is written
down. This session may only reach the hosts its network rules allow. A hop
to any other host is written down as "blocked here", not as dead.

Every link gets one line in links.jsonl. The script can be stopped and
started again: a link that already has a line is not asked again.

    python3 fixtures/probe_p5/check_links.py            # ask until nothing is left
    python3 fixtures/probe_p5/check_links.py --follow   # also wait for probe.py to finish
    python3 fixtures/probe_p5/check_links.py --finish-blocked
        # first go on from the hop where a link stopped because the next
        # host was not allowed for the session (after that host is allowed).
        # The hops already asked are not asked again.
"""

import json
import pathlib
import re
import sys
import time
import urllib.parse

import requests

HERE = pathlib.Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = HERE / "links.jsonl"
GAP = 1.5
TIMEOUT = 45
TRIES = 3
REFUSALS_TO_STOP = 8
MAX_HOPS = 8
# A plain name with no project or person in it.
HEADERS = {"User-Agent": "link-check/1.0 (python-requests; one request at a time)",
           "Accept": "*/*"}
HEAD_REFUSED = (400, 401, 403, 405, 406, 501)  # then GET is tried
SLOW_DOWN = (429, 503)

session = requests.Session()
session.headers.update(HEADERS)
next_time = {}  # host -> the earliest moment it may be asked again
gap = {}  # host -> its gap in seconds
refused_in_a_row = {}
stopped_hosts = set()


def now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def host_of(url: str) -> str:
    return urllib.parse.urlsplit(url).netloc.lower()


def card_links() -> dict:
    """link -> how many cards show it, over every results file there is."""
    links = {}
    for file in sorted(RESULTS.glob("*.json")):
        try:
            result = json.loads(file.read_text(encoding="utf-8"))
        except ValueError:
            continue  # probe.py is still writing it
        for card in result["cards"]:
            if card["source"]:
                links[card["source"]] = links.get(card["source"], 0) + 1
    return links


def one_request(method: str, url: str) -> dict:
    """One HEAD or GET, no redirects followed. -> what happened."""
    host = host_of(url)
    wait = next_time.get(host, 0) - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    step = {"method": method, "url": url, "at": now()}
    try:
        response = session.request(method, url, allow_redirects=False, timeout=TIMEOUT,
                                   stream=True)
        step["status"] = response.status_code
        if response.is_redirect or response.is_permanent_redirect:
            step["location"] = response.headers.get("Location")
        if response.status_code in SLOW_DOWN:
            step["retry_after"] = response.headers.get("Retry-After")
        response.close()  # the page itself is never read
    except requests.exceptions.ProxyError as error:
        code = re.search(r"Tunnel connection failed: (\d+)", str(error))
        step["error"] = "proxy"
        step["proxy_status"] = int(code.group(1)) if code else None
        step["detail"] = str(error)[:200]
    except requests.exceptions.SSLError as error:
        step["error"], step["detail"] = "tls", str(error)[:200]
    except requests.exceptions.ConnectTimeout as error:
        step["error"], step["detail"] = "connect_timeout", str(error)[:200]
    except requests.exceptions.ReadTimeout as error:
        step["error"], step["detail"] = "read_timeout", str(error)[:200]
    except requests.exceptions.ConnectionError as error:
        text = str(error)
        dns = "NameResolutionError" in text or "Name or service not known" in text \
            or "getaddrinfo failed" in text
        step["error"], step["detail"] = ("dns" if dns else "connection"), text[:200]
    except requests.RequestException as error:
        step["error"], step["detail"] = type(error).__name__, str(error)[:200]
    next_time[host] = time.monotonic() + gap.setdefault(host, GAP)
    return step


def polite_request(method: str, url: str, steps: list) -> dict:
    """one_request, but waits and tries again if the host or the proxy says
    it is busy. Every try is written down in steps."""
    host = host_of(url)
    for attempt in range(TRIES):
        step = one_request(method, url)
        steps.append(step)
        busy_host = step.get("status") in SLOW_DOWN
        busy_proxy = step.get("error") == "proxy" and step.get("proxy_status") in (408, 429, 503)
        if not (busy_host or busy_proxy):
            return step
        pause = 60 * (attempt + 1)
        if str(step.get("retry_after") or "").isdigit():
            pause = min(int(step["retry_after"]), 300)
        if busy_host:
            gap[host] = min(gap.get(host, GAP) * 2, 30)  # slow down for this host
        print(f"    {host} says slow down ({step.get('status') or step.get('proxy_status')}), "
              f"waiting {pause} s", flush=True)
        time.sleep(pause)
    return step


def check(url: str, start: str = None, steps: list = None) -> dict:
    """Ask for one link. -> its line for links.jsonl.

    start and steps are only given by --finish-blocked: the hop where an
    earlier try had to stop, and the requests already made."""
    steps = list(steps or [])
    current = start or url
    method = "HEAD"
    step = {}
    for _hop in range(MAX_HOPS + 1):
        if not current.startswith("https://"):
            outcome = "redirects_to_a_plain_http_link_not_followed"
            break
        step = polite_request(method, current, steps)
        if method == "HEAD" and (step.get("status") in HEAD_REFUSED
                                 or step.get("error") in ("connection", "read_timeout")):
            method = "GET"  # HEAD was refused: GET, once
            step = polite_request(method, current, steps)
        if "location" in step and step["location"]:
            current = urllib.parse.urljoin(current, step["location"])
            continue
        outcome = None
        break
    else:
        outcome = "too_many_redirects"

    status = step.get("status")
    if outcome is None:
        if step.get("error") == "proxy" and step.get("proxy_status") in (403, 407):
            outcome = "blocked_here" if current == url else "redirects_to_a_host_blocked_here"
        elif step.get("error") == "dns":
            outcome = "dead_dns_failure"
        elif step.get("error"):
            outcome = "could_not_ask_" + step["error"]
        elif status in (404, 410):
            outcome = "dead_" + str(status)
        elif status in SLOW_DOWN:
            outcome = "host_kept_saying_slow_down"
        elif 200 <= status < 300:
            outcome = "ok"
        else:
            outcome = "other_status"
    return {"url": url, "host": host_of(url), "outcome": outcome, "final_status": status,
            "final_url": current, "final_host": host_of(current),
            "hops": sum(1 for s in steps if s.get("location")), "steps": steps}


def main() -> int:
    follow = "--follow" in sys.argv
    done = set()
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            done.add(json.loads(line)["url"])
    asked = 0
    if "--finish-blocked" in sys.argv and OUT.exists():
        kept = [json.loads(line) for line in OUT.read_text(encoding="utf-8").splitlines()]
        for number, line in enumerate(kept):
            if line["outcome"] == "redirects_to_a_host_blocked_here":
                earlier = [s for s in line["steps"] if s.get("error") != "proxy"]
                kept[number] = check(line["url"], line["final_url"], earlier)
                asked += 1
                OUT.write_text("".join(json.dumps(k) + "\n" for k in kept), encoding="utf-8")
        print(f"{now()} went on with {asked} links that had stopped at a blocked host", flush=True)
    while True:
        links = card_links()
        waiting = [url for url in links if url not in done]
        if not waiting:
            if follow and not (HERE / "runs.json").exists():
                time.sleep(30)  # probe.py is still working
                continue
            break
        by_host = {}
        for url in waiting:
            by_host.setdefault(host_of(url), []).append(url)
        # Take one link from the host that has waited longest, then look again.
        for _ in range(200):
            ready = [h for h in by_host if by_host[h]]
            if not ready:
                break
            host = min(ready, key=lambda h: next_time.get(h, 0))
            url = by_host[host].pop(0)
            if host in stopped_hosts:
                line = {"url": url, "host": host, "outcome": "not_asked_host_kept_refusing",
                        "final_status": None, "final_url": url, "final_host": host,
                        "hops": 0, "steps": []}
            else:
                line = check(url)
                asked += 1
                refused = line["outcome"] in ("host_kept_saying_slow_down",) or \
                    line["outcome"].startswith("could_not_ask_")
                refused_in_a_row[host] = refused_in_a_row.get(host, 0) + 1 if refused else 0
                if refused_in_a_row[host] >= REFUSALS_TO_STOP:
                    stopped_hosts.add(host)
                    print(f"    {host} refused {REFUSALS_TO_STOP} links in a row. "
                          "Leaving it alone.", flush=True)
            with OUT.open("a", encoding="utf-8") as out:
                out.write(json.dumps(line) + "\n")
            done.add(url)
            if asked and asked % 50 == 0:
                print(f"{now()} asked {asked}, lines {len(done)}, "
                      f"waiting about {len(waiting)}", flush=True)
    print(f"{now()} finished. Links asked this run: {asked}. Lines in all: {len(done)}. "
          f"Hosts left alone: {sorted(stopped_hosts)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
