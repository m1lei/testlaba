from fastapi import FastAPI, HTTPException


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """
    Возвращает метрики разработки проекта.
    Кросс-платформенная реализация (macOS/Linux/Windows).
    """
    import subprocess
    import sys
    from datetime import datetime, timezone

    try:
        # Кросс-платформенные флаги для subprocess
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        # Получаем количество коммитов
        commits = subprocess.check_output(
            ["git", "rev-list", "--count", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
            **kwargs
        ).strip()

        # Получаем список авторов
        authors_raw = subprocess.check_output(
            ["git", "shortlog", "-sn"],
            stderr=subprocess.DEVNULL,
            text=True,
            **kwargs
        ).strip().split("\n")

        authors = [
            {"commits": int(a.split()[0]), "name": " ".join(a.split()[1:])}
            for a in authors_raw if a.strip()
        ]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_commits": int(commits),
            "active_authors": len(authors),
            "top_contributors": authors[:5],
            "platform": sys.platform  # 'darwin' для macOS
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Git command failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Metrics collection failed: {str(e)}"
        )