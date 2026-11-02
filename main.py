from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from auth import check_credentials, get_current_user, login_user, logout_user
import data_service

app = FastAPI()
templates = Jinja2Templates(directory=str(Path(__file__).with_name('templates')))


def require_user(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url='/login', status_code=302)
    return user


@app.get('/')
def index():
    return RedirectResponse(url='/trips', status_code=302)


@app.get('/trips', response_class=HTMLResponse)
def show_trips(
    request: Request,
    page: int = 1,
    trip_id: str | None = None,
    l: int | None = None,
    r: int | None = None,
    bench: int | None = None
):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    page_trips, current_page, total_pages = data_service.get_trips_page(page)

    search_result = None
    if trip_id:
        trip, hash_ms, linear_ms = data_service.find_trip_by_id(trip_id)
        search_result = {'trip': trip, 'hash_ms': hash_ms, 'linear_ms': linear_ms}

    query_result = None
    if l is not None and r is not None:
        try:
            ql, qr, st_sum, st_ms, naive_sum, naive_ms = data_service.query_duration_range(l, r)
            query_result = {
                'l': ql, 'r': qr,
                'st_sum': st_sum, 'st_ms': st_ms,
                'naive_sum': naive_sum, 'naive_ms': naive_ms
            }
        except ValueError as error:
            query_result = {'error': str(error)}

    benchmark_result = None
    if bench == 1:
        benchmark_result = data_service.run_benchmark_test()

    return templates.TemplateResponse(
        request=request,
        name='dashboard.html',
        context={
            'user': user,
            'trips': page_trips,
            'page': current_page,
            'total_pages': total_pages,
            'total_rows': len(data_service.trips),
            'hash_stats': data_service.hash_index.stats(),
            'hash_build_ms': data_service.hash_build_ms,
            'segment_build_ms': data_service.segment_build_ms,
            'search_result': search_result,
            'query_result': query_result,
            'benchmark': benchmark_result
        }
    )


@app.get('/trips/{trip_id}', response_class=HTMLResponse)
def trip_info(request: Request, trip_id: str):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    trip, hash_ms, linear_ms = data_service.find_trip_by_id(trip_id)
    if trip is None:
        return RedirectResponse(url='/trips', status_code=302)

    return templates.TemplateResponse(
        request=request,
        name='trip.html',
        context={
            'trip': trip,
            'hash_ms': hash_ms,
            'linear_ms': linear_ms,
            'user': user
        }
    )


@app.post('/trips/{trip_id}/update')
def update_trip(request: Request, trip_id: str, trip_duration: int = Form()):
    user = require_user(request)
    if isinstance(user, RedirectResponse):
        return user

    trip, _, _ = data_service.find_trip_by_id(trip_id)
    if trip is None:
        return RedirectResponse(url='/trips', status_code=302)
    try:
        data_service.update_trip_duration(trip.row_id, trip_duration)
    except ValueError:
        return RedirectResponse(url=f'/trips/{trip_id}?error=invalid_duration', status_code=303)

    return RedirectResponse(url=f'/trips/{trip_id}?updated=1', status_code=303)


@app.get('/login', response_class=HTMLResponse)
def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={'error': error}
    )


@app.post('/api/login')
def login(request: Request, username: str = Form(), password: str = Form()):
    if not check_credentials(username, password):
        return RedirectResponse(url='/login?error=wrong', status_code=302)
    response = RedirectResponse(url='/trips', status_code=302)
    login_user(response, username)
    return response


@app.post('/api/logout')
def logout(request: Request):
    response = RedirectResponse(url='/login', status_code=302)
    logout_user(request, response)
    return response