from django.conf import settings
import ipinfo
from django.shortcuts import render
import socket

import re

def is_domain(value):
    # Regular expression pattern for domain validation
    domain_pattern = r'^([a-zA-Z0-9]+(-[a-zA-Z0-9]+)*\.)+[a-zA-Z]{2,}$'
    return re.match(domain_pattern, value) is not None

def is_ip_address(value):
    # Regular expression pattern for IP address validation
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    return re.match(ip_pattern, value) is not None


def get_ip_address(domain_name):
    try:
        ip_address = socket.gethostbyname(domain_name)
        return ip_address
    except socket.gaierror:
        # Handle error if the domain name is invalid or cannot be resolved
        return None


'''Get IP Details With Custom IP Address'''

def get_ip_details(ip_address=None):
	ipinfo_token = getattr(settings, "IPINFO_TOKEN", None)
	ipinfo_settings = getattr(settings, "IPINFO_SETTINGS", {})
	ip_data = ipinfo.getHandler(ipinfo_token, **ipinfo_settings)
	ip_data = ip_data.getDetails(ip_address)
	return ip_data


'''Index Page'''

def index(request):
    ip_info = None

    if request.method == 'POST':
        ip_address = request.POST.get('ip_address')

        if is_domain(ip_address):
            # It's a domain
            ip_addr = get_ip_address(domain_name=ip_address)
            if ip_addr is not None:
                ip_info = get_ip_details(ip_address=ip_addr)
        elif is_ip_address(ip_address):
            # It's an IP address
            ip_info = get_ip_details(ip_address=ip_address)
        else:
            # Invalid input
            ip_info = None
    else:
        ip_info = request.ipinfo
    
    if ip_info is None:
        error_message = "No IP details found."
        context = {
            'ip_details': None,
            'error_message': error_message
        }
    else:
        details = ip_info.details
        ip = ip_info.ip
        city = details.get('city')
        region = details.get('region')
        country_code = details.get('country')
        country = details.get('country_name')
        loc = details.get('loc')
        org = details.get('org')
        timezone = details.get('timezone')
        asn = details.get('asn')
        company_name = details.get('company').get('name') if details.get('company') else None
        privacy_vpn = details.get('privacy').get('vpn') if details.get('privacy') else None
        abuse_email = details.get('abuse').get('email') if details.get('abuse') else None

        ip_details = {
            'IP': ip,
            'City': city,
            'Region': region,
            'Country_Code': country_code,
            'Country': country,
            'Location': loc,
            'Organization': org,
            'Timezone': timezone,
            'ASN': asn, # Autonomous System Number
            'Company_Name': company_name,
            'Privacy_VPN': privacy_vpn, # Indicates whether the IP address is associated with a VPN 
            'Abuse_Email': abuse_email # Specifies the email address for reporting abuse related to the IP address.
        }
    
        context = {
            'ip_details': ip_details
        }

    template_name = 'index.html'
    return render(request, template_name, context=context)