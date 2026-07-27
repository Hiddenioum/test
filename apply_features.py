#!/usr/bin/env python3
import os
import sys

def main():
    print("Applying custom features via strict Python replacer...")
    # File: Telegram/SourceFiles/api/api_send_progress.cpp
    if os.path.exists('Telegram/SourceFiles/api/api_send_progress.cpp'):
        with open('Telegram/SourceFiles/api/api_send_progress.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if '	const auto requestId = _session->api().request(MTPmessages_SetTyping(' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/api/api_send_progress.cpp")
        content = content.replace('	const auto requestId = _session->api().request(MTPmessages_SetTyping(', '	if (key.history && key.history->ghostModeActive()) {\n		return;\n	}\n	const auto requestId = _session->api().request(MTPmessages_SetTyping(', 1)
        with open('Telegram/SourceFiles/api/api_send_progress.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/api/api_send_progress.cpp' + " successfully.")
    # File: Telegram/SourceFiles/core/core_settings.cpp
    if os.path.exists('Telegram/SourceFiles/core/core_settings.cpp'):
        with open('Telegram/SourceFiles/core/core_settings.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if '		stream >> _thirdSectionInfoShown\n			>> _loopAnimatedStickers;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/core/core_settings.cpp")
        content = content.replace('		stream >> _thirdSectionInfoShown\n			>> _loopAnimatedStickers;', '		stream >> _thirdSectionInfoShown\n			>> _loopAnimatedStickers;\n		stream >> _pausedForUi\n			>> _silentForUi;', 1)
        if '		<< _thirdSectionInfoShown\n		<< _loopAnimatedStickers;' not in content:
            raise RuntimeError(f"Target string hunk 1 not found in Telegram/SourceFiles/core/core_settings.cpp")
        content = content.replace('		<< _thirdSectionInfoShown\n		<< _loopAnimatedStickers;', '		<< _thirdSectionInfoShown\n		<< _loopAnimatedStickers;\n		<< _pausedForUi\n		<< _silentForUi;', 1)
        with open('Telegram/SourceFiles/core/core_settings.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/core/core_settings.cpp' + " successfully.")
    # File: Telegram/SourceFiles/core/core_settings.h
    if os.path.exists('Telegram/SourceFiles/core/core_settings.h'):
        with open('Telegram/SourceFiles/core/core_settings.h', "r", encoding="utf-8") as f:
            content = f.read()
        if '	void setLoopAnimatedStickers(bool loop);\n	[[nodiscard]] bool loopAnimatedStickers() const;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/core/core_settings.h")
        content = content.replace('	void setLoopAnimatedStickers(bool loop);\n	[[nodiscard]] bool loopAnimatedStickers() const;', '	void setLoopAnimatedStickers(bool loop);\n	[[nodiscard]] bool loopAnimatedStickers() const;\n\n	void setPausedForUi(bool paused) { _pausedForUi = paused; }\n	[[nodiscard]] bool pausedForUi() const { return _pausedForUi; }\n	void setSilentForUi(bool silent) { _silentForUi = silent; }\n	[[nodiscard]] bool silentForUi() const { return _silentForUi; }', 1)
        if '	bool _thirdSectionInfoShown = false;\n	bool _loopAnimatedStickers = true;' not in content:
            raise RuntimeError(f"Target string hunk 1 not found in Telegram/SourceFiles/core/core_settings.h")
        content = content.replace('	bool _thirdSectionInfoShown = false;\n	bool _loopAnimatedStickers = true;', '	bool _thirdSectionInfoShown = false;\n	bool _loopAnimatedStickers = true;\n	bool _pausedForUi = false;\n	bool _silentForUi = false;', 1)
        with open('Telegram/SourceFiles/core/core_settings.h', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/core/core_settings.h' + " successfully.")
    # File: Telegram/SourceFiles/data/data_histories.cpp
    if os.path.exists('Telegram/SourceFiles/data/data_histories.cpp'):
        with open('Telegram/SourceFiles/data/data_histories.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'void Histories::sendReadRequest(not_null<History*> history, State &state) {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/data/data_histories.cpp")
        content = content.replace('void Histories::sendReadRequest(not_null<History*> history, State &state) {', 'void Histories::sendReadRequest(not_null<History*> history, State &state) {\n	if (history->ghostModeActive()) {\n		state.willReadTill = 0;\n		state.willReadWhen = 0;\n		return;\n	}', 1)
        with open('Telegram/SourceFiles/data/data_histories.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/data/data_histories.cpp' + " successfully.")
    # File: Telegram/SourceFiles/data/data_session.cpp
    if os.path.exists('Telegram/SourceFiles/data/data_session.cpp'):
        with open('Telegram/SourceFiles/data/data_session.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if '	std::vector<not_null<HistoryItem*>> toDestroy;\n	std::set<not_null<History*>> historiesToCheck;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/data/data_session.cpp")
        content = content.replace('	std::vector<not_null<HistoryItem*>> toDestroy;\n	std::set<not_null<History*>> historiesToCheck;', '	for (const auto id : ids) {\n		if (const auto item = message(id)) {\n			item->setLocallyDeleted(true);\n		}\n	}\n	std::vector<not_null<HistoryItem*>> toDestroy;\n	std::set<not_null<History*>> historiesToCheck;', 1)
        with open('Telegram/SourceFiles/data/data_session.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/data/data_session.cpp' + " successfully.")
    # File: Telegram/SourceFiles/dialogs/dialogs_inner_widget.cpp
    if os.path.exists('Telegram/SourceFiles/dialogs/dialogs_inner_widget.cpp'):
        with open('Telegram/SourceFiles/dialogs/dialogs_inner_widget.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if '		if ((modifiers & Qt::ControlModifier) && (modifiers & Qt::AltModifier) && pressed) {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/dialogs/dialogs_inner_widget.cpp")
        content = content.replace('		if ((modifiers & Qt::ControlModifier) && (modifiers & Qt::AltModifier) && pressed) {', '		if ((modifiers & Qt::ControlModifier) && (modifiers & Qt::AltModifier) && pressed) {\n			if (const auto history = _pressed ? _pressed->history() : nullptr) {\n				history->setGhostModeActive(!history->ghostModeActive());\n				update();\n			}\n		}', 1)
        with open('Telegram/SourceFiles/dialogs/dialogs_inner_widget.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/dialogs/dialogs_inner_widget.cpp' + " successfully.")
    # File: Telegram/SourceFiles/history/history.cpp
    if os.path.exists('Telegram/SourceFiles/history/history.cpp'):
        with open('Telegram/SourceFiles/history/history.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'History::~History() = default;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/history/history.cpp")
        content = content.replace('History::~History() = default;', 'History::~History() = default;\n\nvoid History::setGhostModeActive(bool active) {\n	_ghostModeActive = active;\n}\n\nbool History::ghostModeActive() const {\n	return _ghostModeActive;\n}', 1)
        with open('Telegram/SourceFiles/history/history.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/history/history.cpp' + " successfully.")
    # File: Telegram/SourceFiles/history/history.h
    if os.path.exists('Telegram/SourceFiles/history/history.h'):
        with open('Telegram/SourceFiles/history/history.h', "r", encoding="utf-8") as f:
            content = f.read()
        if '	Data::Folder *folder() const override;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/history/history.h")
        content = content.replace('	Data::Folder *folder() const override;', '	Data::Folder *folder() const override;\n\n	void setGhostModeActive(bool active) { _ghostModeActive = active; }\n	[[nodiscard]] bool ghostModeActive() const { return _ghostModeActive; }', 1)
        if '	std::optional<Data::Folder*> _folder;' not in content:
            raise RuntimeError(f"Target string hunk 1 not found in Telegram/SourceFiles/history/history.h")
        content = content.replace('	std::optional<Data::Folder*> _folder;', '	std::optional<Data::Folder*> _folder;\n	bool _ghostModeActive = false;', 1)
        with open('Telegram/SourceFiles/history/history.h', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/history/history.h' + " successfully.")
    # File: Telegram/SourceFiles/history/history_item.cpp
    if os.path.exists('Telegram/SourceFiles/history/history_item.cpp'):
        with open('Telegram/SourceFiles/history/history_item.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'HistoryItem::~HistoryItem() = default;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/history/history_item.cpp")
        content = content.replace('HistoryItem::~HistoryItem() = default;', 'HistoryItem::~HistoryItem() = default;\n\nbool HistoryItem::locallyDeleted() const {\n	return _locallyDeleted;\n}\n\nvoid HistoryItem::setLocallyDeleted(bool deleted) {\n	_locallyDeleted = deleted;\n}', 1)
        with open('Telegram/SourceFiles/history/history_item.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/history/history_item.cpp' + " successfully.")
    # File: Telegram/SourceFiles/history/history_item.h
    if os.path.exists('Telegram/SourceFiles/history/history_item.h'):
        with open('Telegram/SourceFiles/history/history_item.h', "r", encoding="utf-8") as f:
            content = f.read()
        if '	[[nodiscard]] bool out() const;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/history/history_item.h")
        content = content.replace('	[[nodiscard]] bool out() const;', '	[[nodiscard]] bool out() const;\n\n	[[nodiscard]] bool locallyDeleted() const;\n	void setLocallyDeleted(bool deleted);', 1)
        if '	MsgId _id = 0;' not in content:
            raise RuntimeError(f"Target string hunk 1 not found in Telegram/SourceFiles/history/history_item.h")
        content = content.replace('	MsgId _id = 0;', '	MsgId _id = 0;\n	bool _locallyDeleted = false;', 1)
        with open('Telegram/SourceFiles/history/history_item.h', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/history/history_item.h' + " successfully.")
    # File: Telegram/SourceFiles/history/history_item_components.h
    if os.path.exists('Telegram/SourceFiles/history/history_item_components.h'):
        with open('Telegram/SourceFiles/history/history_item_components.h', "r", encoding="utf-8") as f:
            content = f.read()
        if 'struct EditRevision {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/history/history_item_components.h")
        content = content.replace('struct EditRevision {', 'struct HistoryMessageEditRevisions {\n	std::vector<EditRevision> list;\n};\n\nstruct EditRevision {', 1)
        with open('Telegram/SourceFiles/history/history_item_components.h', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/history/history_item_components.h' + " successfully.")
    # File: Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp
    if os.path.exists('Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp'):
        with open('Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'void TopBarWidget::paintEvent(QPaintEvent *e) {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp")
        content = content.replace('void TopBarWidget::paintEvent(QPaintEvent *e) {', 'void TopBarWidget::paintEvent(QPaintEvent *e) {\n	if (const auto history = _activeChat.key.owningHistory()) {\n		if (history->ghostModeActive()) {\n			p.setFont(st::dialogsTextFont);\n			p.setPen(st::dialogsNameFg);\n			p.drawText(nameleft + namewidth - 80, nametop, u"👻 Ghost"_q);\n		}\n	}', 1)
        with open('Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/history/view/history_view_top_bar_widget.cpp' + " successfully.")
    # File: Telegram/SourceFiles/main/main_account.cpp
    if os.path.exists('Telegram/SourceFiles/main/main_account.cpp'):
        with open('Telegram/SourceFiles/main/main_account.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'void Account::setPausedForUi(bool paused) {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/main/main_account.cpp")
        content = content.replace('void Account::setPausedForUi(bool paused) {', 'void Account::setPausedForUi(bool paused) {\n	_settings.setPausedForUi(paused);\n}\n\nbool Account::pausedForUi() const {\n	return _settings.pausedForUi();\n}\n\nvoid Account::setSilentForUi(bool silent) {\n	_settings.setSilentForUi(silent);\n}', 1)
        with open('Telegram/SourceFiles/main/main_account.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/main/main_account.cpp' + " successfully.")
    # File: Telegram/SourceFiles/main/main_account.h
    if os.path.exists('Telegram/SourceFiles/main/main_account.h'):
        with open('Telegram/SourceFiles/main/main_account.h', "r", encoding="utf-8") as f:
            content = f.read()
        if '	void setPausedForUi(bool paused);' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/main/main_account.h")
        content = content.replace('	void setPausedForUi(bool paused);', '	void setPausedForUi(bool paused);\n	[[nodiscard]] bool pausedForUi() const;\n	void setSilentForUi(bool silent);\n	[[nodiscard]] bool silentForUi() const;', 1)
        with open('Telegram/SourceFiles/main/main_account.h', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/main/main_account.h' + " successfully.")
    # File: Telegram/SourceFiles/main/main_domain.cpp
    if os.path.exists('Telegram/SourceFiles/main/main_domain.cpp'):
        with open('Telegram/SourceFiles/main/main_domain.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'void Domain::setAccountPaused(not_null<Account*> account, bool paused) {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/main/main_domain.cpp")
        content = content.replace('void Domain::setAccountPaused(not_null<Account*> account, bool paused) {', 'void Domain::setAccountPaused(not_null<Account*> account, bool paused) {\n	account->setPausedForUi(paused);\n}\n\nvoid Domain::setAccountSilent(not_null<Account*> account, bool silent) {\n	account->setSilentForUi(silent);\n}', 1)
        with open('Telegram/SourceFiles/main/main_domain.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/main/main_domain.cpp' + " successfully.")
    # File: Telegram/SourceFiles/main/main_domain.h
    if os.path.exists('Telegram/SourceFiles/main/main_domain.h'):
        with open('Telegram/SourceFiles/main/main_domain.h', "r", encoding="utf-8") as f:
            content = f.read()
        if '	void setAccountPaused(not_null<Account*> account, bool paused);' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/main/main_domain.h")
        content = content.replace('	void setAccountPaused(not_null<Account*> account, bool paused);', '	void setAccountPaused(not_null<Account*> account, bool paused);\n	void setAccountSilent(not_null<Account*> account, bool silent);', 1)
        with open('Telegram/SourceFiles/main/main_domain.h', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/main/main_domain.h' + " successfully.")
    # File: Telegram/SourceFiles/settings/sections/settings_information.cpp
    if os.path.exists('Telegram/SourceFiles/settings/sections/settings_information.cpp'):
        with open('Telegram/SourceFiles/settings/sections/settings_information.cpp', "r", encoding="utf-8") as f:
            content = f.read()
        if 'void Information::addImportTdataButton() {' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/settings/sections/settings_information.cpp")
        content = content.replace('void Information::addImportTdataButton() {', 'void Information::addImportTdataButton() {\n	addSettingsButton(\n		container,\n		rpl::single(QString("Import tdata folder")),\n		st::settingsButton,\n		[] { chooseImportFolder(); });\n}', 1)
        with open('Telegram/SourceFiles/settings/sections/settings_information.cpp', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/settings/sections/settings_information.cpp' + " successfully.")
    # File: Telegram/SourceFiles/window/window.style
    if os.path.exists('Telegram/SourceFiles/window/window.style'):
        with open('Telegram/SourceFiles/window/window.style', "r", encoding="utf-8") as f:
            content = f.read()
        if 'menuIconFg: windowSubTextFg;' not in content:
            raise RuntimeError(f"Target string hunk 0 not found in Telegram/SourceFiles/window/window.style")
        content = content.replace('menuIconFg: windowSubTextFg;', 'menuIconFg: windowSubTextFg;\nghostIcon: icon {{ "menu/ghost", menuIconFg }};', 1)
        with open('Telegram/SourceFiles/window/window.style', "w", encoding="utf-8") as f:
            f.write(content)
        print("Patched " + 'Telegram/SourceFiles/window/window.style' + " successfully.")
    print("All custom features applied successfully!")

if __name__ == "__main__":
    main()
