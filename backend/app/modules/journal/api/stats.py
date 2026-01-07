from datetime import datetime, timedelta
import json
from collections import Counter, defaultdict
from fastapi import APIRouter, HTTPException
from backend.app.config import RAW_DIARY_JSON

router = APIRouter()

@router.get("")
def stats():
    """
    Devuelve estadísticas agregadas y tendencias semanales.
    """
    stats_data = {
        "total_entries": 0,
        "emotion_counts": {},
        "top_emotions": [],
        "month_emotions": {},
        "weekly_trends": {
            "dates": [],
            "datasets": []
        }
    }

    if not RAW_DIARY_JSON.exists():
        return stats_data

    try:
        data = json.loads(RAW_DIARY_JSON.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            return stats_data
            
        stats_data["total_entries"] = len(data)
        
        # Contadores globales
        all_emotions = []
        current_month = datetime.now().strftime("%Y-%m")
        month_emotions = []
        
        # Estructuras para tendencias
        today = datetime.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        trends_map = {d.strftime("%d-%m-%Y"): [] for d in last_7_days}
        
        # Etiquetas para el frontend (Lun, Mar...)
        dias_semana_esp = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        stats_data["weekly_trends"]["dates"] = [dias_semana_esp[d.weekday()] for d in last_7_days]

        for entry in data:
            emotions = entry.get("emotions", [])
            if not emotions: continue
            if isinstance(emotions, str): emotions = [emotions]
            
        # Mapeo de normalización para asegurar consistencia
        normalization_map = {
            "felicidad": "alegría",
            "feliz": "alegría",
            "emocionado": "alegría",
            "emocionante": "alegría",
            "tranquilidad": "calma",
            "paz": "calma",
            "estrés": "ansiedad",
            "nervios": "ansiedad",
            "tristeza": "tristeza",
            "miedo": "miedo",
            "inseguridad": "miedo",
            "frustración": "frustración",
            "enojo": "enojo",
            "aburrimiento": "aburrimiento",
            "aburrido": "aburrimiento"
        }

        def normalize_emotion(e):
            e = e.lower().strip()
            return normalization_map.get(e, e)

        for entry in data:
            emotions = entry.get("emotions", [])
            if not emotions: continue
            if isinstance(emotions, str): emotions = [emotions]
            
            # Limpiar y normalizar
            clean_emotions = [normalize_emotion(e) for e in emotions if isinstance(e, str)]
            all_emotions.extend(clean_emotions)
            
            entry_date_str = entry.get("fecha") 
            if entry_date_str:
                fecha_obj = None
                # Intentar format YYYY-MM-DD (nuevo standard)
                try:
                    fecha_obj = datetime.strptime(entry_date_str, "%Y-%m-%d")
                except ValueError:
                    # Intentar DD-MM-YYYY (legacy posible)
                    try:
                        fecha_obj = datetime.strptime(entry_date_str, "%d-%m-%Y")
                    except ValueError:
                        pass
                
                if fecha_obj:
                    # Mes actual
                    if fecha_obj.strftime("%Y-%m") == current_month:
                        month_emotions.extend(clean_emotions)
                        
                    # Tendencias (si está en los últimos 7 días)
                    # Convertir fecha_obj a DD-MM-YYYY para machear con keys de trends_map
                    key_date = fecha_obj.strftime("%d-%m-%Y")
                    if key_date in trends_map:
                        trends_map[key_date].extend(clean_emotions)

        # Calcular frecuencias globales
        counter_global = Counter(all_emotions)
        stats_data["emotion_counts"] = dict(counter_global)
        
        # Calcular frecuencias de los últimos 7 días para el gráfico
        recent_emotions = []
        for ems in trends_map.values():
            recent_emotions.extend(ems)
        counter_recent = Counter(recent_emotions)

        # Usar las top 3 recientes para el gráfico si existen, si no las globales
        chart_emotions = [e[0] for e in counter_recent.most_common(3)]
        if not chart_emotions:
            chart_emotions = [e[0] for e in counter_global.most_common(3)]
        
        stats_data["top_emotions"] = [
            {"name": k, "value": v} 
            for k, v in counter_global.most_common(5)
        ]
        stats_data["month_emotions"] = dict(Counter(month_emotions))

        # Construir datasets para el gráfico
        datasets = []
        colores = ["#818cf8", "#c084fc", "#60a5fa"] # Colores que usa el front
        
        for i, emotion in enumerate(chart_emotions):
            data_points = []
            for date_obj in last_7_days:
                date_str = date_obj.strftime("%d-%m-%Y")
                # Contar ocurrencias de ESTA emoción en ESTE día
                count = trends_map[date_str].count(emotion)
                # Normalizar: porcentaje sobre el TOTAL de emociones de ese día
                total_day = len(trends_map[date_str])
                val = (count / total_day * 100) if total_day > 0 else 0
                data_points.append(round(val))
            
            datasets.append({
                "label": emotion.capitalize(),
                "data": data_points,
                "borderColor": colores[i % len(colores)],
            })
            
        stats_data["weekly_trends"]["datasets"] = datasets

    except Exception as e:
        print(f"Error calculating stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return stats_data
