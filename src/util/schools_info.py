VALID_SCHOOLS = [
    "hkr",
    "mau",
    "oru",
    # "ltu",
    "hig",
    # "sh",
    "hv",
    "hb",
    "mdh",
]

SCHOOL_BASE_URLS = {
    "hkr": "schema.hkr.se",
    "mau": "schema.mau.se",
    "oru": "schema.oru.se",
    # ! "ltu": "schema.ltu.se", COMPLETELY BLOCKED OFF BECAUSE LOGIN REQUIRED
    "hig": "schema.hig.se",
    # ! "sh": "kronox.sh.se", COMPLETELY BLOCKED OFF BECAUSE LOGIN REQUIRED
    "hv": "schema.hv.se",
    "hb": "schema.hb.se",
    "mdh": "webbschema.mdh.se",  # ! LOGIN REQUIRED FOR PROGRAMMES
    # Konstfack school on kronox' website, but can't find schedule page
}
