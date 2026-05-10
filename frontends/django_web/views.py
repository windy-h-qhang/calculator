import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.advanced_math_core import AdvancedMathEngine
from backend.calculator_core import SafeCalculator
from backend.currency_core import CurrencyRateService
from backend.date_core import DateCalculator
from backend.persistence import get_store
from backend.programmer_core import ProgrammerCalculatorEngine
from backend.settings_core import SettingsService
from backend.unit_converter import UnitConverter


def index(request):
    return render(request, "calculator.html")


@csrf_exempt
@require_POST
def calculate(request):
    data = request_json(request)
    expression = data.get("expression", "")
    try:
        result = SafeCalculator.calculate(expression)
        get_store().add_history("standard", expression, result)
        return JsonResponse({"ok": True, "result": result})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def advanced_math(request):
    data = request_json(request)
    try:
        result = AdvancedMathEngine.calculate(
            data.get("operation", "求导"),
            data.get("expression", ""),
            variable=data.get("variable", "x"),
            order=data.get("order", 2),
            point=data.get("point", 0),
            lower=data.get("lower", ""),
            upper=data.get("upper", ""),
        )
        get_store().add_history("advanced", data.get("expression", ""), result.get("exact", ""), result)
        return JsonResponse({"ok": True, **result})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def programmer(request):
    data = request_json(request)
    try:
        value = ProgrammerCalculatorEngine.evaluate(
            data.get("expression", ""),
            data.get("base", "DEC"),
            data.get("word_size", "QWORD"),
            bool(data.get("signed", False)),
        )
        rows = ProgrammerCalculatorEngine.conversion_rows(
            value,
            data.get("word_size", "QWORD"),
            bool(data.get("signed", False)),
        )
        get_store().add_history("programmer", data.get("expression", ""), rows.get(data.get("base", "DEC"), value))
        return JsonResponse({"ok": True, "value": value, "rows": rows})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def currency(request):
    data = request_json(request)
    try:
        amount = float(data.get("amount", 1))
        rate = CurrencyRateService.fetch_rate(
            data.get("base", "USD"),
            data.get("quote", "CNY"),
        )
        converted = amount * rate["rate"]
        get_store().add_history(
            "currency",
            f"{amount} {rate['base']}",
            f"{converted:.4f} {rate['quote']}",
            rate,
        )
        return JsonResponse(
            {
                "ok": True,
                "amount": amount,
                "converted": converted,
                **rate,
            }
        )
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def unit_convert(request):
    data = request_json(request)
    try:
        result = UnitConverter.convert(
            data.get("value", 0),
            data.get("category", "长度"),
            data.get("from_unit", "米"),
            data.get("to_unit", "千米"),
        )
        get_store().add_history(
            "unit",
            f"{data.get('value', 0)} {data.get('from_unit')}",
            f"{result} {data.get('to_unit')}",
            {"category": data.get("category")},
        )
        return JsonResponse({"ok": True, "result": result})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


def unit_catalog(request):
    return JsonResponse(
        {
            "ok": True,
            "categories": {
                category: UnitConverter.units(category)
                for category in UnitConverter.categories()
            },
        }
    )


@csrf_exempt
@require_POST
def date_calculate(request):
    data = request_json(request)
    try:
        operation = data.get("operation", "difference")
        if operation == "add_days":
            result = DateCalculator.add_days(
                data.get("start"),
                int(data.get("days", 0)),
                bool(data.get("weekdays_only", False)),
            )
            expression = "加减天数"
            output = result["result"]
        else:
            result = DateCalculator.difference(
                data.get("start"),
                data.get("end"),
                bool(data.get("include_end", False)),
            )
            expression = "日期差"
            output = f"{result['days']} 天"
        get_store().add_history("date", expression, output, result)
        return JsonResponse({"ok": True, **result})
    except Exception as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)


@csrf_exempt
def settings_view(request):
    if request.method == "GET":
        return JsonResponse({"ok": True, "settings": SettingsService.get_settings()})
    data = request_json(request)
    return JsonResponse({"ok": True, "settings": SettingsService.update_settings(data)})


def history(request):
    category = request.GET.get("category")
    return JsonResponse({"ok": True, "items": get_store().list_history(category, 50)})


def request_json(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))
