from flask import Blueprint, render_template, request, redirect, url_for, flash


main = Blueprint("main", __name__)


@main.route("/")
def index():
    return "<h1>Hello, REST API.</h1>"
