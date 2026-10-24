import argparse
import json
import logging
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

IP_PATTERN = re.compile(
    r"^(?:(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])\.){3}"
    r"(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$"
)
MAC_PATTERN = re.compile(r"^(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})$")

logger = logging.getLogger(__name__)


@dataclass
class ArpEntry:
    ip: str
    mac: str
    interface: str
    entry_type: str


@dataclass
class ArpSpoofing:
    mac_spoofing: str
    ip_associated: list[str]
    severity: str = "CRITICAL"
    description: str = "POSSIBLE MAN-IN-THE-MIDDLE / ARP-SPOOFING ATTACK IN PROGRESS!"


def parse_arp_file(file_path: Path) -> tuple[list[ArpEntry], int]:
    valid_entries = []
    invalid_count = 0

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    start_index = 1 if lines and (
        "IP" in lines[0].upper() or "MAC" in lines[0].upper()) else 0

    for line in lines[start_index:]:
        if not line.strip():
            continue

        parts = line.strip().split(",")

        if len(parts) >= 2:
            ip = parts[0].strip()
            mac = parts[1].strip()
            interface = parts[2].strip() if len(parts) >= 3 else "unknown"
            entry_type = parts[3].strip() if len(parts) >= 4 else "unknown"

            if IP_PATTERN.match(ip) and MAC_PATTERN.match(mac):
                valid_entries.append(ArpEntry(ip, mac, interface, entry_type))
            else:
                invalid_count += 1

    return valid_entries, invalid_count


def detect_spoofing(entries: list[ArpEntry]) -> list[ArpSpoofing]:
    mac_to_ip = defaultdict(set)
    attack = []

    for entry in entries:
        mac_to_ip[entry.mac].add(entry.ip)

    for mac, ip in mac_to_ip.items():
        if len(ip) > 1:
            attack.append(ArpSpoofing(
                mac_spoofing=mac,
                ip_associated=sorted(ip)
            ))

    return attack


def setup_logging(log_file: str):
    log_format = "[%(levelname)s] %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding="utf-8")
        ]
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Варіант 11: Аудитор ARP-таблиць та виявлення ARP-Spoofing"
    )
    parser.add_argument("--arp-file", required=True,
                        help="Шлях до файлу з ARP-таблицею (CSV)")
    parser.add_argument("--output-json", required=True,
                        help="Шлях для збереження JSON-звіту")
    parser.add_argument(
        "--detect-spoofing", action="store_true",
        help="Увімкнути пошук ARP-Spoofing")
    parser.add_argument("--log-file", default="arp_audit.log",
                        help="Шлях до файлу логування")

    return parser.parse_args()


def main():
    args = parse_arguments()
    setup_logging(args.log_file)

    arp_path = Path(args.arp_file)
    if not arp_path.exists():
        logger.error(f"File not found: {arp_path}")
        return

    logger.info(f"Parsing ARP table snapshot from {arp_path}...")

    valid_entries, invalid_count = parse_arp_file(arp_path)

    logger.info(f"Validated {len(valid_entries)} IP/MAC entries.")

    print("\n=== Validated Entries Summary ===")
    print(f"Valid IP/MAC Pairs : {len(valid_entries)}")
    print(f"Invalid Syntax     : {invalid_count}")

    if args.detect_spoofing:
        logger.info("Running ARP-Spoofing detection analysis...")
        alerts = detect_spoofing(valid_entries)

        print("\n=== CRITICAL SECURITY ALERTS: ARP-SPOOFING DETECTED ===")

        if alerts:
            for alert in alerts:
                print("[ALERT] MAC Address Duplicate Conflict!")
                print(
                    f"MAC Address: {alert.mac_spoofing} associated with MULTIPLE IP addresses:")

                for ip in alert.ip_associated:
                    tag = "(Default Gateway)" if ip.endswith(
                        ".1") else "(Suspicious Host)"
                    print(f"  - {ip} {tag}")

                print(f"  -> {alert.description}")

                logger.warning(
                    f"ARP-Spoofing detected: MAC {alert.mac_spoofing} mapped to IPs {alert.ip_associated}"
                )
        else:
            print("No spoofing detected. Network ARP table appears clean.")
            logger.info("No spoofing detected.")

        report = {
            "total_valid": len(valid_entries),
            "total_invalid": invalid_count,
            "spoofing_alerts": [asdict(alert) for alert in alerts]
        }

        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=4, ensure_ascii=False)

        logger.info(f"Critical conflict logged to {output_path}")


if __name__ == "__main__":
    main()
