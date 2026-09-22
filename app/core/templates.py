from __future__ import annotations

from fastapi.templating import Jinja2Templates

from app.core.config import settings
from app.core.formatting import current_year, format_datetime_ar


templates = Jinja2Templates(directory=str(settings.templates_dir))
templates.env.filters["datetime_ar"] = format_datetime_ar
templates.env.globals["current_year"] = current_year
