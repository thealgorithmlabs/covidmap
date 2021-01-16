import math

import requests
import scrapy

# Street used for a simple example
street = "VICENTE@BLASCO@IBA%c3%91EZ"

# categories: Residencial, Almacén-Estacionamiento, Comercial, Oficinas, OcioyHostelería, Cultural, Industrial
# restaurante: 2m2 por persona en el 40% del espacio. 12 camareros por comensal
# http://www.eqa-ecu.es/EQA/doc/DB-SIjun2016.pdf


def compute_infection_risk(room_surface=100, duration=90, place="Class", infective_people=1):

    if place=="Master-Choir":
        ventilation_outside_air = 0.7
        decay_rate_virus = 0.62
        deposition_surfaces = 0.3
        additional_control = 0
        height = 5
        quanta_exhalation_rate_infected = 970
        exhalation_mask_efficiency = 0
        fraction_people_mask = 0
        inhalation_mask_efficiency = 0
        breathing_rate = 1.56
    elif place=="Class":
        ventilation_outside_air = 3
        decay_rate_virus = 0.62
        deposition_surfaces = 0.3
        additional_control = 0
        height = 3
        quanta_exhalation_rate_infected = 25
        exhalation_mask_efficiency = 50.0
        fraction_people_mask = 100.0
        inhalation_mask_efficiency = 30.0
        breathing_rate = 0.52
    elif place=="Subway":
        ventilation_outside_air = 5.7
        decay_rate_virus = 0.62
        deposition_surfaces = 0.3
        additional_control = 3.6
        height = 2
        quanta_exhalation_rate_infected = 25
        exhalation_mask_efficiency = 50.0
        fraction_people_mask = 100.0
        inhalation_mask_efficiency = 30.0
        breathing_rate = 0.42
    elif place=="Supermkt":
        ventilation_outside_air = 3
        decay_rate_virus = 0.62
        deposition_surfaces = 0.3
        additional_control = 0
        height = 5
        quanta_exhalation_rate_infected = 10
        exhalation_mask_efficiency = 50.0
        fraction_people_mask = 100.0
        inhalation_mask_efficiency = 30.0
        breathing_rate = 0.72
    elif place=="Stadium":
        ventilation_outside_air = 40
        decay_rate_virus = 0.62
        deposition_surfaces = 0.3
        additional_control = 0
        height = 15
        quanta_exhalation_rate_infected = 50
        exhalation_mask_efficiency = 0
        fraction_people_mask = 0
        inhalation_mask_efficiency = 0
        breathing_rate = 0.72
    else:
        ventilation_outside_air = 3
        decay_rate_virus = 0.62
        deposition_surfaces = 0.3
        additional_control = 0
        height = 3
        quanta_exhalation_rate_infected = 25
        exhalation_mask_efficiency = 50.0
        fraction_people_mask = 100.0
        inhalation_mask_efficiency = 30.0
        breathing_rate = 0.52

    room_volume = height * room_surface

    total_first_order_loss_rate = ventilation_outside_air + decay_rate_virus + deposition_surfaces + additional_control
    net_emission_rate = quanta_exhalation_rate_infected * (1-exhalation_mask_efficiency*fraction_people_mask) *infective_people

    avg_quantaconcentration = (net_emission_rate/total_first_order_loss_rate/room_volume) * (1-(
        1/total_first_order_loss_rate/duration
    ))*(1-math.exp(-1*(total_first_order_loss_rate*duration)))

    quanta_inhaled_per_person = avg_quantaconcentration * breathing_rate * duration * (1-inhalation_mask_efficiency*fraction_people_mask)
    probability_infection = 1-math.exp(quanta_inhaled_per_person)

    return probability_infection


def compute_density(item):
    density = 0
    if item["category"] == "OcioyHostelería":
        clients = (item["surface"] * 0.4) / 2
        if clients >= 12:
            staff = round((clients / 12)) + round(clients/24)
        else:
            staff = 3
        density = (staff+clients) / item["surface"]
    elif item["category"] == "Industrial" or item["category"] == "Oficinas":
        staff = (item["surface"] * 0.9) / 4
        density = staff/item["surface"]
    elif item["category"] == "Almacén-Estacionamiento":
        staff = item["surface"] / 8
        density = staff / item["surface"]
    elif item["category"] == "Residencial":
        staff = item["surface"] / 20
        density = staff / item["surface"]
    elif item["category"] == "Comercial":
        clients = (item["surface"] * 0.6) / 2
        staff = (item["surface"] * 0.4) / 10
        density = (staff+clients) / item["surface"]
    elif item["category"] == "Cultural":
        clients = item["surface"] * 0.8
        staff = (item["surface"] * 0.2) / 4
        density = (staff + clients) / item["surface"]
    return density


def compute_closest_service(props, pos):
    services = ["Cultural", "Comercial", "OcioyHostelería"]
    left = pos - 1
    right = pos + 1
    found = False
    dist = 1
    while not found and (left >= 0 or right <= len(props)):
        found_left = False
        found_right = False
        if left >= 0:
            dist = abs(pos-left) * 20
            found_left = props[left]["category"] in services
        elif right < len(props):
            dist = abs(pos-right) * 20
            found_right = props[right]["category"] in services

        found = found_left or found_right
        left -= 1
        right += 1
    return pow(dist, -1/2)


def compute():
    props = get_street_buildings(start=42, end=52)
    services = ["Cultural", "Comercial", "OcioyHostelería"]
    i = 0
    for prop in props:
        # calc density
        density = prop["surface"]
        # extract N neighbors
        density = compute_density(prop)
        list_copy = props.copy()

        if i < 5:
            neighbors = props[0:10]
            del list_copy[0:10]
        elif i+5 < len(props):
            neighbors = props[len(props)-10:len(props)]
            del list_copy[len(list_copy)-10:len(list_copy)]
        else:
            neighbors = props[i-5:i+5]
            del list_copy[i-5:i+5]
        i += 1

        for neighbor in neighbors:
            density += compute_density(neighbor)

        if prop["category"] in services:
            j = 1
            sub_density = 0
            for p in list_copy:
                if i != j:
                    dist = pow(abs((i-j) * 20), (-1/2))
                    sub_density += dist * compute_density(p)
                j += 1

        else:
            j = 1
            sub_density = 0
            for p in props:
                if i != j:
                    dist = pow(abs((i - j) * 20), (-1 / 2))
                    sub_density += dist * compute_density(p)
                j += 1
            sub_density = (1/8) * sub_density
            sub_density = sub_density * compute_closest_service(props, i)
        density += sub_density

        density += sub_density

        print("Building: " + prop["category"] + "  " +
              str(prop["street_num"]) + " " + str(prop["surface"]) + " density: " + str(density))


def get_street_buildings(start, end):
    parcels = []
    for n in range(start, end, 2):
        val=n
        query_url = """
        https://www1.sedecatastro.gob.es/CYCBienInmueble/OVCListaBienes.aspx?via=GRAN@VIA&tipoVia=CL&numero={num}&kilometro=&bloque=&escalera=&planta=&puerta=&DescProv=MADRID&prov=28&muni=900&DescMuni=MADRID&TipUR=U&codvia=3097&comVia=GRAN%20VIA%20(CALLE)&pest=urbana&from=OVCBusqueda&nomusu=%20&tipousu=&ZV=NO&ZR=NO        """.format(num=val)
        street_items = get_properties_address(query_url, number=n)
        if street_items:
            parcels += street_items
    return parcels


def get_properties_address(query_url, number):
    q_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Content-Type": "application/json; charset=UTF-8"
    }
    rr = requests.get(url=query_url, headers=q_headers
                       )
    get_properties = '//div[@class="panel-heading"]//' \
                     'div[@class="panel-title texto_regular gray9 float-right"]' \
                     '//span[@data-toggle="tooltip"]/text()'
    res = scrapy.Selector(text=rr.text).xpath(get_properties).extract()
    index = 0
    items = []
    category = ""
    surface = 0

    for r in res:
        if index == 0:
            name = (r.replace(" ", ""))

        elif index == 1:
            surface = int((r.replace(" ", "").replace("m", "").replace(".", "")))
            obj = {"category": name, "surface": surface, "street_num": number}
            items.append(obj)

        if index == 3:
            index = 0
        else:
            index += 1

    return items