import argparse
import logging
import sys
from xml.etree import ElementTree as ET

from modules import parser

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--inputfile', '-if', type=str, required=True, help='Path to input .nessus file')
PARSER.add_argument('--outputfile', '-of', type=str, default='./compliance_results.csv', help='Path to output CSV file')
PARSER.add_argument('--outputdelim', '-od', type=str, default=',', help='Output file delimiter (default: "%(default)s")')
PARSER.add_argument('--urls', '-u', action='store_true', help='Only print things with http:// or https:// URI')
PARSER.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

ARGS = PARSER.parse_args()

if ARGS.verbose:
    logging.basicConfig(format='%(message)s', level=logging.DEBUG, stream=sys.stderr)
else:
    logging.basicConfig(format='%(message)s', level=logging.INFO, stream=sys.stderr)


def main():
    logging.info(f"[i] Reading file from: {ARGS.inputfile}")
    try:
        # get document root
        xml_doc = ET.parse(ARGS.inputfile).getroot()
        service_uris = list()
        # iterate through all Report elements within the provided .nessus file
        for report in xml_doc.findall('Report'):
            report_hosts = parser.parse_hosts(report)

            report_issues = list()
            for host in report_hosts:
                logging.debug(f"[i] Collecting services for host: {host.get('name')}")
                services = parser.parse_services(host)
                if services:
                    tcp_services = list(filter(lambda x: x.protocol == 'tcp', services))
                    udp_services = list(filter(lambda x: x.protocol == 'udp', services))
                    logging.debug(f"[i] Found {len(tcp_services)} TCP and {len(udp_services)} UDP service(s)")

                    for service in services:
                        if (ARGS.urls and service.uri in ['http://', 'https://']) or not ARGS.urls:
                            service_uris.append(f"{service.uri}{service.hostname}:{service.port}")
                else:
                    logging.debug(f"[i] No services found")

            # sort issues by name
            # report_issues = sorted(report_issues, key=lambda x: x.name)
            # headers = ['Host', 'Check Name', 'Configured Value', 'Expected Value', 'Info', 'Solution', 'Result']
            # output.write_output(ARGS.outputfile, headers, report_issues, ARGS.outputdelim)
            # logging.info(f"[i] Output file written to: {ARGS.outputfile}")

        for uri in service_uris:
            print(uri)

    except Exception as err:
        logging.error(f"[!] {err}")


if __name__ == '__main__':
    main()
