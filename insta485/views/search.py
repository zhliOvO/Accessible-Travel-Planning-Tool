"""Module for handling the 'Post' feature in the Insta485 app."""
import os
import pathlib
import flask
from flask import session, abort, jsonify
import arrow
import insta485

@insta485.app.route('/search')
def search_page():
    """Render the search page."""
    return flask.render_template('search.html')

@insta485.app.route('/get_services', methods=['GET'])
def get_services():
    disability_type = flask.request.args.get('disability_type')
    connection = insta485.model.get_db()
    cursor = connection.execute(
        "SELECT feature_name FROM AccessibilityFeatures WHERE disability_type = ?",
        (disability_type,)
    )
    services = cursor.fetchall()
    return jsonify(services)

@insta485.app.route('/search_hotels', methods=['POST'])
def search_hotels():
    """Search for hotels that provide all selected services."""
    selected_services = flask.request.json.get('services', [])
    if not selected_services:
        return jsonify([])

    connection = insta485.model.get_db()

    # Get feature_ids for the selected services
    placeholders = ', '.join('?' for _ in selected_services)
    feature_ids_query = (
        f"SELECT feature_id FROM AccessibilityFeatures "
        f"WHERE feature_name IN ({placeholders})"
    )
    cursor = connection.execute(feature_ids_query, selected_services)
    feature_ids = [row['feature_id'] for row in cursor.fetchall()]

    if not feature_ids:
        return jsonify([])

    # Find hotels that have all the selected features
    placeholders = ', '.join('?' for _ in feature_ids)
    query = (
        f"SELECT hotel_name FROM Hotels "
        f"WHERE hotel_id IN ("
        f"  SELECT hotel_id FROM HotelAccessibility "
        f"  WHERE feature_id IN ({placeholders}) "
        f"  GROUP BY hotel_id "
        f"  HAVING COUNT(DISTINCT feature_id) = ?"
        f")"
    )
    cursor = connection.execute(query, (*feature_ids, len(feature_ids)))
    hotels = cursor.fetchall()
    return jsonify(hotels)
