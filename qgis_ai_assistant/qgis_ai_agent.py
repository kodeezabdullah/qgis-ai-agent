# -*- coding: utf-8 -*-
import os.path
import traceback

from qgis.PyQt.QtCore import Qt, QCoreApplication, QLocale, QTranslator
from qgis.PyQt.QtGui import QIcon

try:
    from qgis.PyQt.QtGui import QAction
except ImportError:
    from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsSettings

SETTINGS_KEY = "qgis_ai_agent/api_key"


def _dock_area_right():
    area = getattr(Qt, "RightDockWidgetArea", None)
    if area is not None:
        return area
    return Qt.DockWidgetArea.RightDockWidgetArea


class QgisAiAgent:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        try:
            locale = QgsSettings().value("locale/userLocale", QLocale().name())[0:2]
            locale_path = os.path.join(self.plugin_dir, "i18n", f"{locale}.qm")
            if os.path.exists(locale_path):
                self.translator = QTranslator()
                self.translator.load(locale_path)
                QCoreApplication.installTranslator(self.translator)
        except Exception as e:
            print(f"[QgisAiAgent] locale init failed: {e}")

        self.actions = []
        self.menu = self.tr("&QGIS AI Agent")
        self.dock_widget = None
        self.toolbar_action = None
        self._agent = None
        self._agent_key = None

    def tr(self, message):
        return QCoreApplication.translate("QgisAiAgent", message)

    def initGui(self):
        print("[QgisAiAgent] initGui()")
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        action = QAction(QIcon(icon_path), self.tr("QGIS AI Agent"), self.iface.mainWindow())
        action.setCheckable(True)
        action.triggered.connect(self.toggle_dock)
        self.iface.addToolBarIcon(action)
        self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)
        self.toolbar_action = action
        print("[QgisAiAgent] toolbar action installed")

    def unload(self):
        print("[QgisAiAgent] unload()")
        if self.dock_widget is not None:
            try:
                self.iface.removeDockWidget(self.dock_widget)
                self.dock_widget.deleteLater()
            except Exception as e:
                print(f"[QgisAiAgent] removeDockWidget failed: {e}")
            self.dock_widget = None

        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        self.actions = []

    def _get_agent(self):
        key = QgsSettings().value(SETTINGS_KEY, "") or ""
        if not key:
            self._agent = None
            self._agent_key = None
            return None
        if self._agent is None or self._agent_key != key:
            try:
                from .agent.agent import QgisAiAgent as AgentCore
                self._agent = AgentCore(api_key=key)
                self._agent_key = key
            except Exception as e:
                print(f"[QgisAiAgent] agent init failed: {e}")
                traceback.print_exc()
                self._agent = None
                self._agent_key = None
                return None
        return self._agent

    def _ensure_dock(self):
        if self.dock_widget is not None:
            return True
        try:
            from .ui.dock_widget import QgisAiAgentDockWidget
            print("[QgisAiAgent] creating dock widget...")
            self.dock_widget = QgisAiAgentDockWidget(
                agent_provider=self._get_agent,
                parent=self.iface.mainWindow(),
            )
            self.iface.addDockWidget(_dock_area_right(), self.dock_widget)
            self.dock_widget.visibilityChanged.connect(self._on_dock_visibility)
            print("[QgisAiAgent] dock widget added to right area")
            return True
        except Exception as e:
            print(f"[QgisAiAgent] _ensure_dock failed: {e}")
            traceback.print_exc()
            self.iface.messageBar().pushWarning(
                "QGIS AI Agent",
                f"Failed to open panel: {e}",
            )
            return False

    def _on_dock_visibility(self, visible):
        if self.toolbar_action is not None:
            self.toolbar_action.setChecked(visible)

    def toggle_dock(self, checked=False):
        print(f"[QgisAiAgent] toggle_dock(checked={checked})")
        if not self._ensure_dock():
            if self.toolbar_action is not None:
                self.toolbar_action.setChecked(False)
            return

        if self.dock_widget.isVisible():
            self.dock_widget.hide()
        else:
            self.dock_widget.show()
            self.dock_widget.raise_()
