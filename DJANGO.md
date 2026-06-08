# StageLink Django

This project includes a Django interface that preserves the existing CLI
workflow. The original Python modules live in `stagelink_core/` and remain the
source of the application logic; Django starts `main.py` and sends browser input
to the same prompts.

## Run

```bash
pip install -r requirements.txt
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

The original console workflow is still available:

```bash
python main.py
```

## Structure

```text
manage.py
main.py
stagelink_site/
stagelink_core/
  admin.py
  authentification.py
  data.py
  data.json
  entreprise.py
  etudiant.py
  evenements.py
  main.py
  storage.py
webterminal/
```
