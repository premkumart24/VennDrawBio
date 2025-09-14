from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt

from venn import venn
import io
import base64
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")


from fastapi.staticfiles import StaticFiles

# mount the static directory at /static
app.mount("/static", StaticFiles(directory="static"), name="static")



@app.get("/", response_class=HTMLResponse)
def serve_frontend(request: Request):
    return templates.TemplateResponse("venndrawbio_frontend.html", {"request": request})


@app.post("/venn")
async def venn_diagram(values: dict):
    """
    Accepts JSON mapping label -> list-or-string.
    Input is flexible: comma/space/newline-separated, or a JSON list.
    Case-insensitive matching (APP == app).
    Returns JSON with venn image (base64) and exact intersections.
    """
    try:
        sets = {}
        case_map = {}  
        for k, v in (values or {}).items():
            if isinstance(v, str):
                items = [x.strip() for x in re.split(r"[,\s;]+", v) if x.strip()]
            elif isinstance(v, (list, tuple, set)):
                items = [str(x).strip() for x in v if str(x).strip()]
            else:
                items = [str(v).strip()]

            normed = set(i.lower() for i in items)
            sets[k] = normed
            for orig in items:
                case_map.setdefault(orig.lower(), orig)

        if not sets:
            return JSONResponse(status_code=400, content={"error": "No sets provided"})

        plt.figure(figsize=(6, 6))
        venn(sets)
        buf = io.BytesIO()
        plt.savefig(buf, bbox_inches="tight", format="png")
        plt.close()
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode("ascii")
        data_uri = f"data:image/png;base64,{img_b64}"



        membership = {}
        for label, s in sets.items():
            for elem in s:
                membership.setdefault(elem, set()).add(label)


        all_labels = list(sets.keys())

        from itertools import combinations

        combo_map = {}  

        n = len(all_labels)

        for r in range(2, n + 1):
            for combo in combinations(all_labels, r):
                combo_set = set(combo)
                key = " and ".join(combo)   
                items = []
                for elem_lower, labels_for_elem in membership.items():
                    if labels_for_elem.issuperset(combo_set):
                        pretty_elem = case_map.get(elem_lower, elem_lower)
                        items.append(pretty_elem)
                if items:
                    unique_sorted = sorted(set(items), key=lambda s: s.lower())
                    combo_map[key] = unique_sorted

        exact_map = combo_map

        return {"image": data_uri, "intersections": exact_map}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
