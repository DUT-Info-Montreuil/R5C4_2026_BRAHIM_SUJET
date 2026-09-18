import sqlite3
from flask import Flask, jsonify, request

app = Flask(__name__)
DB_NAME = "parties.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/api/v1/referentiels", methods=["GET"])
def get_referentiels():
    """Route pour obtenir les référentiels (ex: liste des jeux, etc.)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        jeux = [
            row["nom"]
            for row in cursor.execute(
                "SELECT DISTINCT nom FROM jeux ORDER BY nom"
            ).fetchall()
        ]
    except sqlite3.OperationalError:
        jeux = []

    conn.close()
    return jsonify({"jeux": jeux})


@app.route("/api/v1/parties", methods=["GET"])
def get_parties():
    jeu = request.args.get("jeu")
    tri = request.args.get("tri", "id")
    ordre = request.args.get("ordre", "asc").lower()

    try:
        limit = int(request.args.get("limit", 10))
        page = int(request.args.get("page", 1))
        offset = (page - 1) * limit
    except ValueError:
        return jsonify({"error": "Paramètres de pagination invalides"}), 400

    if ordre not in ["asc", "desc"]:
        ordre = "asc"

    # Colonnes réellement disponibles après jointure
    # parties.file_id -> files.id -> files.jeu_id -> jeux.id
    # parties.serveur_id -> serveurs.id
    map_tri = {
        "id": "p.id",
        "attente": "p.attente_secondes",
        "duree": "p.duree_minutes",
        "debut": "p.debut",
        "jeu": "j.nom",
        "serveur": "s.nom",
    }
    colonne_tri = map_tri.get(tri, "p.id")

    query = """
        SELECT
            p.id,
            p.debut,
            p.attente_secondes,
            p.duree_minutes,
            s.id AS serveur_id,
            s.nom AS serveur,
            s.region,
            f.id AS file_id,
            f.nom AS file_nom,
            j.id AS jeu_id,
            j.nom AS jeu
        FROM parties p
        JOIN files f ON p.file_id = f.id
        JOIN jeux j ON f.jeu_id = j.id
        JOIN serveurs s ON p.serveur_id = s.id
        WHERE 1=1
    """
    params = []

    if jeu:
        query += " AND j.nom = ?"
        params.append(jeu)

    query += f" ORDER BY {colonne_tri} {ordre.upper()} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        rows = cursor.execute(query, params).fetchall()
    except sqlite3.OperationalError as e:
        conn.close()
        return jsonify({"error": f"Erreur SQL: {e}"}), 500
    conn.close()

    parties = [dict(row) for row in rows]
    return jsonify(
        {"page": page, "limit": limit, "count": len(parties), "data": parties}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)