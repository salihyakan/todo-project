import redis
from django.conf import settings
from datetime import time


def get_redis_connection():
    if settings.IS_DOCKER:
        return redis.Redis(
            host=settings.REDIS_HOST,
            port=6379,
            db=0,
            decode_responses=True
        )
    else:
        return redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

def store_pomodoro_session(user_id, session_type, duration):
    r = get_redis_connection()
    key = f"pomodoro:{user_id}:sessions"
    
    # Store session data as a hash
    session_id = r.incr(f"pomodoro:{user_id}:session_counter")
    session_key = f"session:{session_id}"
    
    r.hset(session_key, "type", session_type)
    r.hset(session_key, "duration", duration)
    r.hset(session_key, "timestamp", int(time.time()))
    
    # Add to user's session list
    r.lpush(key, session_key)
    
    # Update totals
    if session_type == "work":
        r.incrby(f"pomodoro:{user_id}:total_work", duration)
        r.incr(f"pomodoro:{user_id}:completed_count")
    else:
        r.incrby(f"pomodoro:{user_id}:total_break", duration)

def get_pomodoro_stats(user_id):
    r = get_redis_connection()
    return {
        "completed": int(r.get(f"pomodoro:{user_id}:completed_count") or 0),
        "focus_time": int(r.get(f"pomodoro:{user_id}:total_work") or 0),
        "break_time": int(r.get(f"pomodoro:{user_id}:total_break") or 0)
    }

def get_recent_sessions(user_id, count=10):
    r = get_redis_connection()
    key = f"pomodoro:{user_id}:sessions"
    session_keys = r.lrange(key, 0, count-1)
    
    sessions = []
    for session_key in session_keys:
        session_data = r.hgetall(session_key)
        if session_data:
            sessions.append({
                "type": session_data["type"],
                "duration": int(session_data["duration"]),
                "timestamp": int(session_data["timestamp"])
            })
    return sessions