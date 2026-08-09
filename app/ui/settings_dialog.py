"""
Settings and Broker Configuration Modal Dialog.
Allows user to switch between Mock Simulator, Angel One SmartAPI, and Fyers API v3.
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox, QLineEdit, QPushButton, QLabel, QGroupBox, QMessageBox
from PyQt6.QtCore import Qt
from app.config import (
    DEFAULT_MODE, ANGEL_API_KEY, ANGEL_CLIENT_CODE, ANGEL_PASSWORD, ANGEL_TOTP_SECRET,
    FYERS_CLIENT_ID, FYERS_ACCESS_TOKEN
)

class SettingsDialog(QDialog):
    def __init__(self, current_mode: str = DEFAULT_MODE, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Broker Connection & Data Feed Settings")
        self.resize(480, 420)
        self.selected_mode = current_mode
        self.credentials = {}

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(14)

        # Mode Selection
        form_mode = QFormLayout()
        self.cmb_mode = QComboBox()
        self.cmb_mode.addItems(["MOCK (High-Fidelity Simulator)", "ANGEL_ONE (SmartAPI)", "FYERS (API v3)"])

        # Preselect current mode
        if current_mode == "ANGEL_ONE":
            self.cmb_mode.setCurrentIndex(1)
        elif current_mode == "FYERS":
            self.cmb_mode.setCurrentIndex(2)
        else:
            self.cmb_mode.setCurrentIndex(0)

        self.cmb_mode.currentIndexChanged.connect(self._on_mode_changed)
        form_mode.addRow("Active Data Feed Mode:", self.cmb_mode)
        self.layout.addLayout(form_mode)

        # Angel One Group
        self.grp_angel = QGroupBox("Angel One SmartAPI Credentials")
        angel_layout = QFormLayout(self.grp_angel)

        self.txt_angel_key = QLineEdit(ANGEL_API_KEY)
        self.txt_angel_client = QLineEdit(ANGEL_CLIENT_CODE)
        self.txt_angel_pass = QLineEdit(ANGEL_PASSWORD)
        self.txt_angel_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_angel_totp = QLineEdit(ANGEL_TOTP_SECRET)

        angel_layout.addRow("API Key:", self.txt_angel_key)
        angel_layout.addRow("Client Code:", self.txt_angel_client)
        angel_layout.addRow("Password:", self.txt_angel_pass)
        angel_layout.addRow("TOTP Secret:", self.txt_angel_totp)
        self.layout.addWidget(self.grp_angel)

        # Fyers Group
        self.grp_fyers = QGroupBox("Fyers API v3 Credentials")
        fyers_layout = QFormLayout(self.grp_fyers)

        self.txt_fyers_id = QLineEdit(FYERS_CLIENT_ID)
        self.txt_fyers_token = QLineEdit(FYERS_ACCESS_TOKEN)
        self.txt_fyers_token.setEchoMode(QLineEdit.EchoMode.Password)

        fyers_layout.addRow("Client ID:", self.txt_fyers_id)
        fyers_layout.addRow("Access Token:", self.txt_fyers_token)
        self.layout.addWidget(self.grp_fyers)

        # Buttons
        btn_box = QHBoxLayout()
        btn_save = QPushButton("Apply & Connect")
        btn_save.setObjectName("accentButton")
        btn_save.clicked.connect(self._on_save)

        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)

        btn_box.addStretch()
        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        self.layout.addLayout(btn_box)

        self._on_mode_changed(self.cmb_mode.currentIndex())

    def _on_mode_changed(self, index: int):
        if index == 1: # Angel One
            self.grp_angel.setEnabled(True)
            self.grp_fyers.setEnabled(False)
        elif index == 2: # Fyers
            self.grp_angel.setEnabled(False)
            self.grp_fyers.setEnabled(True)
        else: # Mock
            self.grp_angel.setEnabled(False)
            self.grp_fyers.setEnabled(False)

    def _on_save(self):
        idx = self.cmb_mode.currentIndex()
        if idx == 1:
            self.selected_mode = "ANGEL_ONE"
        elif idx == 2:
            self.selected_mode = "FYERS"
        else:
            self.selected_mode = "MOCK"

        self.credentials = {
            "angel_api_key": self.txt_angel_key.text().strip(),
            "angel_client_code": self.txt_angel_client.text().strip(),
            "angel_password": self.txt_angel_pass.text().strip(),
            "angel_totp_secret": self.txt_angel_totp.text().strip(),
            "fyers_client_id": self.txt_fyers_id.text().strip(),
            "fyers_access_token": self.txt_fyers_token.text().strip(),
        }
        self.accept()
