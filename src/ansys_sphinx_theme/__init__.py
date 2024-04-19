# Copyright (C) 2021 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""This is the ansys-sphinx-theme module."""
import logging
import os
import pathlib
from typing import Any, Dict

from docutils.nodes import document
import requests
from sphinx import addnodes
from sphinx.application import Sphinx

from ansys_sphinx_theme.extension.linkcode import DOMAIN_KEYS, sphinx_linkcode_resolve
from ansys_sphinx_theme.latex import generate_404  # noqa: F401

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:  # pragma: no cover
    import importlib_metadata

__version__ = importlib_metadata.version(__name__.replace(".", "-"))


# Declare the fundamental paths of the theme
THIS_PATH = pathlib.Path(__file__).parent.resolve()
THEME_PATH = THIS_PATH / "theme" / "ansys_sphinx_theme"
STATIC_PATH = THEME_PATH / "static"
STYLE_PATH = STATIC_PATH / "css"
JS_PATH = STATIC_PATH / "js"
CSS_PATH = STYLE_PATH / "ansys_sphinx_theme.css"
TEMPLATES_PATH = THEME_PATH / "_templates"
AUTOAPI_TEMPLATES_PATH = TEMPLATES_PATH / "autoapi"
JS_FILE = JS_PATH / "table.js"

# make logo paths available
ansys_favicon = str((STATIC_PATH / "ansys-favicon.png").absolute())
ansys_logo_black = str((STATIC_PATH / "ansys_logo_black_cropped.jpg").absolute())
ansys_logo_white = str((STATIC_PATH / "ansys_logo_white.pdf").absolute())
ansys_logo_white_cropped = str((STATIC_PATH / "ansys_logo_white_cropped.pdf").absolute())
page_404 = str((STATIC_PATH / "404.rst").absolute())
pyansys_logo_black = str((STATIC_PATH / "pyansys-logo-black-cropped.png").absolute())
pyansys_logo_white = str((STATIC_PATH / "pyansys-logo-white-cropped.png").absolute())
watermark = str((STATIC_PATH / "watermark.pdf").absolute())


def get_html_theme_path() -> pathlib.Path:
    """Return list of HTML theme paths.

    Returns
    -------
    pathlib.Path
        Path pointing to the installation directory of the theme.

    """
    return THEME_PATH.resolve()


def get_version_match(semver: str) -> str:
    """Evaluate the version match for the multi-documentation.

    Parameters
    ----------
    semver : str
        Semantic version number in the form of a string.

    Returns
    -------
    str
        Matching version number in the form of a string.

    """
    if "dev" in semver:
        return "dev"
    major, minor, *_ = semver.split(".")
    return ".".join([major, minor])


def get_autoapi_templates_dir_relative_path(path: pathlib.Path) -> str:
    """Return a string representing the relative path for autoapi templates.

    Parameters
    ----------
    path : pathlib.Path
        Path to the desired file.

    Returns
    -------
    str
        A string rerpesenting the relative path to the autoapi templates.

    """
    return os.path.relpath(str(AUTOAPI_TEMPLATES_PATH.absolute()), start=str(path.absolute()))


def add_autoapi_theme_option(app: Sphinx) -> None:
    """Add the autoapi template path to the theme options.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    """
    autoapi = app.config.html_theme_options.get("autoapi", {})
    if not autoapi:
        return
    required_extensions = ["sphinx_jinja", "sphinx_design"]

    for extension in required_extensions:
        if extension not in app.config["extensions"]:
            app.config["extensions"].append(extension)
    print(app.config["extensions"])
    AUTOAPI_OPTIONS = [
        "members",
        "undoc-members",
        "show-inheritance",
        "show-module-summary",
        "special-members",
    ]
    app.add_css_file("https://www.nerdfonts.com/assets/css/webfont.css")
    autoapi_template_dir = autoapi.get("templates", "")
    autoapi_project_name = autoapi.get("project", "")

    if not autoapi_template_dir:
        autoapi_template_dir = get_autoapi_templates_dir_relative_path(app.confdir)

    app.config["autoapi_template_dir"] = autoapi_template_dir

    def prepare_jinja_env(jinja_env) -> None:
        """Prepare the Jinja environment for the theme."""
        jinja_env.globals["project_name"] = autoapi_project_name

    # Set the autoapi options
    app.config["autoapi_prepare_jinja_env"] = prepare_jinja_env
    app.config["autoapi_type"] = autoapi.get("type", "python")
    app.config["autoapi_dirs"] = autoapi.get("directory", [])
    app.config["autoapi_root"] = autoapi.get("output", "api")
    app.config["autoapi_own_page_level"] = autoapi.get("own_page_level", "module")
    app.config["autoapi_python_use_implicit_namespaces"] = autoapi.get(
        "use_implicit_namespaces", True
    )
    app.config["autoapi_keep_files"] = autoapi.get("keep_files", True)
    app.config["autoapi_python_class_content"] = autoapi.get("class_content", "class")
    app.config["autoapi_options"] = autoapi.get("options", AUTOAPI_OPTIONS)


def convert_version_to_pymeilisearch(semver: str) -> str:
    """Convert a semantic version number to pymeilisearch-compatible format.

    This function evaluates the given semantic version number and returns a
    version number that is compatible with `pymeilisearch`, where dots are
    replaced with hyphens.

    Parameters
    ----------
    semver : str
        Semantic version number in the form of a string.

    Returns
    -------
    str
        pymeilisearch-compatible version number.
    """
    version = get_version_match(semver).replace(".", "-")
    return version


def setup_default_html_theme_options(app):
    """Set up the default configuration for the HTML options.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Notes
    -----
    This function is the only way to overwrite ``pydata-sphinx-theme``
    configuration. Variables declared in the ``theme.conf`` do not include
    inherited ones.

    """
    # Place all switchers and icons at the end of the navigation bar
    if app.config.html_theme_options.get("switcher"):
        app.config.html_theme_options.setdefault(
            "navbar_end", ["version-switcher", "theme-switcher", "navbar-icon-links"]
        )
    app.config.html_theme_options.setdefault("collapse_navigation", True)
    app.config.html_theme_options.setdefault("navigation_with_keys", True)


def fix_edit_html_page_context(
    app: Sphinx, pagename: str, templatename: str, context: dict, doctree: document
) -> None:
    """Add a function that Jinja can access for returning an "edit this page" link .

    This function creates an "edit this page" link for any library.
    The link points to the corresponding file on the main branch.

    Parameters
    ----------
    app : Sphinx
        Sphinx application instance for rendering the documentation.
    pagename : str
        Name of the current page.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the page.
    doctree : document
        Document tree for the page.

    Notes
    -----
    .. [1] Originally implemented by `Alex Kaszynski <https://github.com/akaszynski>`_ in
    `PyVista <https://github.com/pyvista/pyvista>`_,
    see https://github.com/pyvista/pyvista/pull/4113
    """

    def fix_edit_link_page(link: str) -> str:
        """Transform "edit on GitHub" links to the correct URL.

        This function fixes the URL for the "edit this page" link.

        Parameters
        ----------
        link : str
            Link to the GitHub edit interface.

        Returns
        -------
        str
            Link to the corresponding file on the main branch.
        """
        github_user = context.get("github_user", "")
        github_repo = context.get("github_repo", "")
        github_source = context.get("source_path", "")
        kind = context.get("github_version", "")

        if "_autosummary" in pagename:
            for obj_node in list(doctree.findall(addnodes.desc)):
                try:
                    domain = obj_node.get("domain")
                    for signode in obj_node:
                        if not isinstance(signode, addnodes.desc_signature):
                            continue
                        # Convert signode to a specified format
                        info = {}
                        for key in DOMAIN_KEYS.get(domain, []):
                            value = signode.get(key)
                            if not value:
                                value = ""
                            info[key] = value
                        if not info:
                            continue
                        # This is an API example
                        return sphinx_linkcode_resolve(
                            domain=domain,
                            info=info,
                            library=f"{github_user}/{github_repo}",
                            source_path=github_source,
                            github_version=kind,
                            edit=True,
                        )
                except ValueError as e:
                    logging.debug(f"An error occurred: {e}")  # Log the exception as debug info
                    return link

        elif pagename in ["autoapi", "api"]:
            for obj_node in list(doctree.findall(addnodes.desc)):
                domain = obj_node.get("domain")
                if domain != "py":
                    return link

                for signode in obj_node:
                    if not isinstance(signode, addnodes.desc_signature):
                        continue

                    fullname = signode["module"]
                    modname = fullname.replace(".", "/")

                    if github_source:
                        return f"http://github.com/{github_user}/{github_repo}/edit/{kind}/{github_source}/{modname}.{domain}"  # noqa: E501
                    else:
                        return f"http://github.com/{github_user}/{github_repo}/edit/{kind}/{modname}.{domain}"  # noqa: E501

        else:
            return link

    context["fix_edit_link_page"] = fix_edit_link_page


def update_footer_theme(
    app: Sphinx, pagename: str, templatename: str, context: Dict[str, Any], doctree: document
) -> None:
    """Update the version number of the Ansys Sphinx theme in the footer.

    Connect to the Sphinx application instance for rendering the documentation,
    and add the current version number of the Ansys Sphinx theme to the page context.
    This allows the theme to update the footer with the current version number.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    pagename : str
        The name of the current page.
    templatename : str
        The name of the template being used.
    context : dict
        The context dictionary for the page.
    doctree : ~docutils.nodes.document
        The document tree for the page.
    """
    context["ansys_sphinx_theme_version"] = __version__


def add_cheat_sheet(
    app: Sphinx, pagename: str, templatename: str, context: Dict[str, Any], doctree: document
) -> None:
    """Add a cheat sheet to the left navigation sidebar.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    pagename : str
        Name of the current page.
    templatename : str
        Name of the template being used.
    context : dict
        Context dictionary for the page.
    doctree : ~docutils.nodes.document
        The doctree.
    """
    cheatsheet_options = app.config.html_theme_options.get("cheatsheet", {})
    pages = cheatsheet_options.get("pages", ["index"])
    pages = [pages] if isinstance(pages, str) else pages
    if cheatsheet_options and any(pagename == page for page in pages):
        if cheatsheet_options.get("needs_download"):
            static_folder = app.config.html_static_path or ["static"]
            download_cheatsheet_to_static(app, cheatsheet_options, static_folder, context)
        sidebar = context.get("sidebars", [])
        sidebar.append("cheatsheet_sidebar.html")
        context["sidebars"] = sidebar


def download_cheatsheet_to_static(
    app: Sphinx,
    cheatsheet_options: Dict[str, Any],
    static_folder: pathlib.Path,
    context: Dict[str, Any],
) -> None:
    """Download the cheatsheet to the static directory.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    cheatsheet_options : dict
        Dictionary containing the cheat sheet options.
    static_folder : pathlib.Path
        Path containing the static folder.
    context : dict
        Dictionary containing the context for the page.
    """
    cheatsheet_url = cheatsheet_options.get("url", "")
    cheatsheet_thumbnail = cheatsheet_options.get("thumbnail", "")
    static_path = pathlib.Path(app.outdir) / static_folder[0]
    context["cheatsheet_static_path"] = str(static_folder[0])

    # Download cheat sheet file if URL is provided
    if cheatsheet_url:
        download_file(cheatsheet_url, static_path)

    # Download cheat sheet image if thumbnail URL is provided
    if cheatsheet_thumbnail:
        download_file(cheatsheet_thumbnail, static_path)


def download_file(url: str, directory: pathlib.Path) -> None:
    """
    Download a file from the given URL and save it to a given directory.

    Parameters
    ----------
    url : str
        URL of the file to download.
    directory : pathlib.Path
        Directory to save the file to.
    """
    filename = url.split("/")[-1]
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
    if not (directory / filename).exists():
        file_path = directory / filename
        with open(file_path, "wb") as file:
            response = requests.get(url)
            if response.status_code != 200:
                raise FileNotFoundError(f"Failed to download file from {url}.")
            file.write(response.content)


def replace_html_tag(app, exception):
    """Replace HTML tags in the generated HTML files.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.
    exception : Exception
        Exception that occurred during the build process.
    """
    if exception is None:
        build_dir = pathlib.Path(app.builder.outdir).resolve()
        file_names = [str(file) for file in build_dir.rglob("*.html")]
        for file_name in file_names:
            with open(build_dir / file_name, "r", encoding="utf-8") as f:
                content = f.read()
            with open(build_dir / file_name, "w", encoding="utf-8") as f:
                f.write(content.replace("&lt;", "<").replace("&gt;", ">"))


def setup(app: Sphinx) -> Dict:
    """Connect to the Sphinx theme app.

    Parameters
    ----------
    app : ~sphinx.application.Sphinx
        Application instance for rendering the documentation.

    Returns
    -------
    Dict
        Dictionary containing application status.

    """
    # Add the theme configuration
    theme_path = get_html_theme_path()
    app.add_html_theme("ansys_sphinx_theme", theme_path)
    app.config.templates_path.append(str(THEME_PATH / "components"))

    # Add default HTML configuration
    setup_default_html_theme_options(app)

    # Verify that the main CSS file exists
    if not CSS_PATH.exists():
        raise FileNotFoundError(f"Unable to locate ansys-sphinx theme at {CSS_PATH.absolute()}")
    app.add_css_file(str(CSS_PATH.relative_to(STATIC_PATH)))
    app.add_js_file(str(JS_FILE.relative_to(STATIC_PATH)))
    app.config.templates_path.append(str(TEMPLATES_PATH))
    app.add_js_file("https://cdn.datatables.net/1.10.23/js/jquery.dataTables.min.js")
    app.add_css_file("https://cdn.datatables.net/1.10.23/css/jquery.dataTables.min.css")
    app.connect("html-page-context", update_footer_theme)
    app.connect("html-page-context", fix_edit_html_page_context)
    app.connect("html-page-context", add_cheat_sheet)
    app.connect("builder-inited", add_autoapi_theme_option, priority=200)
    app.connect("build-finished", replace_html_tag)
    app.connect("doctree-read", update_env)
    app.connect("env-check-consistency", check_consistency)
    app.connect("build-finished", check_config_after_build)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
