import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from backend.advanced_math_core import AdvancedMathEngine
from backend.calculator_core import SafeCalculator
from backend.currency_core import CurrencyRateService
from backend.programmer_core import ProgrammerCalculatorEngine


def index(request):
    return render(request, "calculator.html")


@csrf_exempt
@require_POST
def calculate(request):
    data = request_json(request)
    expression = data.get("expression", "")
    try:
        result = SafeCalculator.calculate(expression)
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


def request_json(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode("utf-8"))
