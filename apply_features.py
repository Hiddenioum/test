#!/usr/bin/env python3
"""
Custom Telegram Desktop feature patcher.
Targets: tdesktop v7.1.3 (and compatible).
"""
import os
import sys

def patch_file(filepath, target, replacement, allow_missing=False):
    if not os.path.exists(filepath):
        if allow_missing:
            print(f"Skipping missing file: {filepath}")
            return False
        raise RuntimeError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if target not in content:
        if allow_missing:
            print(f"Warning: target not found in {filepath}: {repr(target[:80])}")
            return False
        raise RuntimeError(f"Target string not found in {filepath}: {repr(target[:80])}")
    content = content.replace(target, replacement, 1)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Patched {filepath} successfully.")
    return True


def main():
    print("Applying custom features for Telegram Desktop v7.1.3...")

    # =========================================================================
    # 1. Ghost Mode: Block typing indicators (api_send_progress.cpp)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "#include \"api/api_send_progress.h\"",
        "#include \"api/api_send_progress.h\"\n#include \"core/application.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/api/api_send_progress.cpp",
        "\tconst auto requestId = _session->api().request(MTPmessages_SetTyping(",
        "\tif ((key.history && key.history->ghostModeActive()) || Core::App().settings().globalGhostMode()) {\n\t\treturn;\n\t}\n\tconst auto requestId = _session->api().request(MTPmessages_SetTyping("
    )

    # =========================================================================
    # 2. Core Settings: Ghost Mode global flag (core_settings.h)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}",
        "\tvoid setLoopAnimatedStickers(bool value) {\n\t\t_loopAnimatedStickers = value;\n\t}\n\tvoid setGlobalGhostMode(bool ghost) { _globalGhostMode = ghost; }\n\t[[nodiscard]] bool globalGhostMode() const { return _globalGhostMode; }"
    )
    patch_file(
        "Telegram/SourceFiles/core/core_settings.h",
        "\tbool _loopAnimatedStickers = true;",
        "\tbool _loopAnimatedStickers = true;\n\tbool _globalGhostMode = false;"
    )

    # =========================================================================
    # 3. Ghost Mode: Block read receipts (data_histories.cpp)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "#include \"core/application.h\"",
        "#include \"core/application.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/data/data_histories.cpp",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {",
        "void Histories::sendReadRequest(not_null<History*> history, State &state) {\n\tif (history->ghostModeActive() || Core::App().settings().globalGhostMode()) {\n\t\tstate.willReadTill = 0;\n\t\tstate.willReadWhen = 0;\n\t\treturn;\n\t}"
    )

    # =========================================================================
    # 4. Anti-Delete: Mark messages as locally deleted instead of destroying them
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "\tfor (const auto &messageId : data) {\n\t\tconst auto i = list ? list->find(messageId.v) : Messages::iterator();\n\t\tif (list && i != list->end()) {\n\t\t\tconst auto history = i->second->history();\n\t\t\ttoDestroy.push_back(i->second);\n\t\t\thistoriesToCheck.emplace(history);\n\t\t} else if (affected) {\n\t\t\taffected->unknownMessageDeleted(messageId.v);\n\t\t}\n\t}",
        "\tfor (const auto &messageId : data) {\n\t\tif (const auto item = message(peerId, messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}"
    )
    patch_file(
        "Telegram/SourceFiles/data/data_session.cpp",
        "void Session::processNonChannelMessagesDeleted(const QVector<MTPint> &data) {\n\tauto toDestroy = std::vector<not_null<HistoryItem*>>();\n\tauto historiesToCheck = base::flat_set<not_null<History*>>();\n\tfor (const auto &messageId : data) {\n\t\tif (const auto item = nonChannelMessage(messageId.v)) {\n\t\t\tconst auto history = item->history();\n\t\t\ttoDestroy.push_back(item);\n\t\t\thistoriesToCheck.emplace(history);\n\t\t}\n\t}\n\tif (!toDestroy.empty()) {\n\t\tnotifyItemsAboutToBeDestroyed(toDestroy);\n\t\tfor (const auto &item : toDestroy) {\n\t\t\titem->destroy();\n\t\t}\n\t}\n\tfor (const auto &history : historiesToCheck) {\n\t\tif (!history->chatListMessageKnown()) {\n\t\t\thistory->requestChatListMessage();\n\t\t}\n\t}\n}",
        "void Session::processNonChannelMessagesDeleted(const QVector<MTPint> &data) {\n\tfor (const auto &messageId : data) {\n\t\tif (const auto item = nonChannelMessage(messageId.v)) {\n\t\t\titem->setLocallyDeleted(true);\n\t\t}\n\t}\n}"
    )

    # =========================================================================
    # 5. Ghost Mode: Per-chat methods on History
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "#include \"core/ui_integration.h\"",
        "#include \"core/ui_integration.h\"\n#include \"core/core_settings.h\""
    )
    patch_file(
        "Telegram/SourceFiles/history/history.cpp",
        "History::~History() = default;",
        "History::~History() = default;\n\nvoid History::setGhostModeActive(bool active) {\n\t_ghostModeActive = active;\n}\n\nbool History::ghostModeActive() const {\n\treturn _ghostModeActive || Core::App().settings().globalGhostMode();\n}"
    )
    patch_file(
        "Telegram/SourceFiles/history/history.h",
        "\tData::Folder *folder() const override;",
        "\tData::Folder *folder() const override;\n\n\tvoid setGhostModeActive(bool active);\n\t[[nodiscard]] bool ghostModeActive() const;"
    )
    patch_file(
        "Telegram/SourceFiles/history/history.h",
        "\tstd::optional<Data::Folder*> _folder;",
        "\tstd::optional<Data::Folder*> _folder;\n\tbool _ghostModeActive = false;"
    )

    # =========================================================================
    # 6. HistoryItem: locallyDeleted flag + edit toggle fields (header)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\t[[nodiscard]] bool out() const {",
        "\t[[nodiscard]] bool locallyDeleted() const {\n\t\treturn _locallyDeleted;\n\t}\n\tvoid setLocallyDeleted(bool deleted);\n\tvoid toggleOriginalEditVersion();\n\n\t[[nodiscard]] bool out() const {"
    )
    patch_file(
        "Telegram/SourceFiles/history/history_item.h",
        "\tMsgId id;",
        "\tMsgId id;\n\tbool _locallyDeleted = false;\n\tTextWithEntities _originalEditText;\n\tTextWithEntities _editedCurrentText;\n\tbool _showingOriginal = false;"
    )

    # =========================================================================
    # 7. HistoryItem: setLocallyDeleted + toggleOriginalEditVersion (cpp)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "HistoryItem::~HistoryItem() {",
        "void HistoryItem::setLocallyDeleted(bool deleted) {\n\tif (_locallyDeleted != deleted) {\n\t\t_locallyDeleted = deleted;\n\t\thistory()->owner().requestItemResize(this);\n\t}\n}\n\nvoid HistoryItem::toggleOriginalEditVersion() {\n\tif (_originalEditText.text.isEmpty()) {\n\t\treturn;\n\t}\n\t_showingOriginal = !_showingOriginal;\n\tif (_showingOriginal) {\n\t\tsetText(_originalEditText);\n\t} else {\n\t\tsetText(_editedCurrentText);\n\t}\n\thistory()->owner().requestItemTextRefresh(this);\n\thistory()->owner().requestItemResize(this);\n\thistory()->owner().requestItemRepaint(this);\n}\n\nHistoryItem::~HistoryItem() {"
    )

    # Save original text in applyEdition BEFORE the edit is applied
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "\tconst auto &checkedMedia = updatingSavedLocalEdit",
        "\tif (_originalEditText.text.isEmpty()) {\n\t\t_originalEditText = originalText();\n\t}\n\tconst auto &checkedMedia = updatingSavedLocalEdit"
    )

    # Save edited text AFTER setText in applyEdition (v7.1.3 anchor: useSameReplies)
    patch_file(
        "Telegram/SourceFiles/history/history_item.cpp",
        "\t} else {\n\t\tsetText(std::move(updatedText));\n\t\taddToSharedMediaIndex();\n\t}\n\tif (!edition.useSameReplies)",
        "\t} else {\n\t\tsetText(std::move(updatedText));\n\t\t_editedCurrentText = originalText();\n\t\taddToSharedMediaIndex();\n\t}\n\tif (!edition.useSameReplies)"
    )

    # =========================================================================
    # 8. BottomInfo: Add Deleted flag to enum (0x4000 to avoid collision with Updated=0x2000)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.h",
        "\t\t\tEphemeral      = 0x1000,",
        "\t\t\tEphemeral      = 0x1000,\n\t\t\tDeleted        = 0x4000,"
    )

    # =========================================================================
    # 9. BottomInfo: Set Deleted flag in BottomInfoDataFromMessage
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.cpp",
        "\tif (const auto views = item->Get<HistoryMessageViews>()) {",
        "\tif (item->locallyDeleted()) {\n\t\tresult.flags |= Flag::Deleted;\n\t}\n\tif (const auto views = item->Get<HistoryMessageViews>()) {"
    )

    # =========================================================================
    # 10. BottomInfo: Show [Deleted] tag next to timestamp in layoutDateText
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.cpp",
        "\tconst auto full = (_data.flags & Data::Flag::Sponsored)\n\t\t? QString()\n\t\t: (_data.flags & Data::Flag::Imported)\n\t\t? (date + ' ' + tr::lng_imported(tr::now))\n\t\t: name.isEmpty()\n\t\t? date\n\t\t: (name + afterAuthor);",
        "\tconst auto deleted = (_data.flags & Data::Flag::Deleted)\n\t\t? u\"[Deleted] \"_q\n\t\t: QString();\n\tconst auto full = (_data.flags & Data::Flag::Sponsored)\n\t\t? QString()\n\t\t: deleted + ((_data.flags & Data::Flag::Imported)\n\t\t? (date + ' ' + tr::lng_imported(tr::now))\n\t\t: name.isEmpty()\n\t\t? date\n\t\t: (name + afterAuthor));"
    )

    # =========================================================================
    # 11. BottomInfo: Click "Edited" label -> toggle original/current text
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/history/view/history_view_bottom_info.cpp",
        "\tif (inTime) {\n\t\tresult.cursor = CursorState::Date;\n\t}\n\treturn result;\n}",
        "\tif (inTime) {\n\t\tresult.cursor = CursorState::Date;\n\t\tif (_data.flags & Data::Flag::Edited) {\n\t\t\tconst auto item = view->data();\n\t\t\tresult.link = std::make_shared<LambdaClickHandler>([item](ClickContext) {\n\t\t\t\titem->toggleOriginalEditVersion();\n\t\t\t});\n\t\t}\n\t}\n\treturn result;\n}"
    )

    # =========================================================================
    # 12. Main Account: Per-account freeze (pausedForUi) - header
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/main/main_account.h",
        "\tvoid logOut();",
        "\tvoid logOut();\n\tvoid setPausedForUi(bool paused);\n\t[[nodiscard]] bool pausedForUi() const;"
    )
    patch_file(
        "Telegram/SourceFiles/main/main_account.h",
        "\tbool _loggingOut = false;",
        "\tbool _loggingOut = false;\n\tbool _pausedForUi = false;"
    )
    # Per-account freeze - implementation
    patch_file(
        "Telegram/SourceFiles/main/main_account.cpp",
        "void Account::logOut() {",
        "void Account::setPausedForUi(bool paused) {\n\t_pausedForUi = paused;\n}\n\nbool Account::pausedForUi() const {\n\treturn _pausedForUi;\n}\n\nvoid Account::logOut() {"
    )

    # =========================================================================
    # 13. Import tData: Passcode Unlock + Avatar Circle Grid + Deduplication + 1-Click Restart + Keep Add Account
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "#include \"settings/sections/settings_information.h\"",
        "#include \"settings/sections/settings_information.h\"\n#include \"storage/details/storage_file_utilities.h\"\n#include \"core/file_utilities.h\"\n#include \"core/application.h\"\n#include \"ui/toast/toast.h\"\n#include \"ui/boxes/confirm_box.h\"\n#include \"ui/widgets/input_fields.h\"\n#include \"ui/widgets/buttons.h\"\n#include \"ui/widgets/labels.h\"\n#include \"boxes/abstract_box.h\"\n#include \"history/history.h\"\n#include \"data/notify/data_notify_settings.h\"\n#include \"data/notify/data_peer_notify_settings.h\"\n#include <QDir>\n#include <QFile>\n#include <QDirIterator>\n#include <QPainter>"
    )
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        """not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {
\tconst auto result = _outer->add(
\t\tobject_ptr<Ui::SlideWrap<Ui::SettingsButton>>(
\t\t\t_outer.get(),
\t\t\tCreateButtonWithIcon(
\t\t\t\t_outer.get(),
\t\t\t\ttr::lng_menu_add_account(),
\t\t\t\tst::mainMenuAddAccountButton,
\t\t\t\t{
\t\t\t\t\t&st::settingsIconAdd,
\t\t\t\t\tIconType::Round,
\t\t\t\t\t&st::windowBgActive
\t\t\t\t})))->setDuration(0);
\tconst auto button = result->entity();

\tusing Environment = MTP::Environment;
\tconst auto add = [=](Environment environment, bool newWindow = false) {
\t\tauto &domain = _controller->session().domain();
\t\tdomain.removeRedundantAccounts();

\t\tauto found = false;
\t\tfor (const auto &[index, account] : domain.accounts()) {
\t\t\tconst auto raw = account.get();
\t\t\tif (!raw->sessionExists()
\t\t\t\t&& raw->mtp().environment() == environment) {
\t\t\t\tfound = true;
\t\t\t}
\t\t}
\t\tif (!found && domain.accounts().size() >= domain.maxAccounts()) {
\t\t\t_controller->show(
\t\t\t\tBox(AccountsLimitBox, &_controller->session()));
\t\t} else if (newWindow) {
\t\t\tdomain.addActivated(environment, true);
\t\t} else {
\t\t\t_controller->window().preventOrInvoke([=] {
\t\t\t\tCore::App().setActivePrimaryWindow(&_controller->window());
\t\t\t\t_controller->session().domain().addActivated(environment);
\t\t\t});
\t\t}
\t};

\tbutton->setAcceptBoth(true);
\tbutton->clicks(
\t) | rpl::on_next([=](Qt::MouseButton which) {
\t\tif (which == Qt::LeftButton) {
\t\t\tconst auto modifiers = button->clickModifiers();
\t\t\tconst auto newWindow = (modifiers & Qt::ControlModifier);
\t\t\tadd(Environment::Production, newWindow);
\t\t\treturn;
\t\t} else if (which != Qt::RightButton
\t\t\t|| !IsAltShift(button->clickModifiers())) {
#ifdef _DEBUG
\t\t\tif (which != Qt::RightButton) {
\t\t\t\treturn;
\t\t\t}
#else // _DEBUG
\t\t\treturn;
#endif // !_DEBUG
\t\t}
\t\t_contextMenu = base::make_unique_q<Ui::PopupMenu>(_outer);
\t\t_contextMenu->addAction("Production Server", [=] {
\t\t\tadd(Environment::Production);
\t\t});
\t\t_contextMenu->addAction("Test Server", [=] {
\t\t\tadd(Environment::Test);
\t\t});
\t\t_contextMenu->popup(QCursor::pos());
\t}, button->lifetime());

\treturn result;
}""",
        """not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {
\tconst auto result = _outer->add(
\t\tobject_ptr<Ui::SlideWrap<Ui::SettingsButton>>(
\t\t\t_outer.get(),
\t\t\tCreateButtonWithIcon(
\t\t\t\t_outer.get(),
\t\t\t\ttr::lng_menu_add_account(),
\t\t\t\tst::mainMenuAddAccountButton,
\t\t\t\t{
\t\t\t\t\t&st::settingsIconAdd,
\t\t\t\t\tIconType::Round,
\t\t\t\t\t&st::windowBgActive
\t\t\t\t})))->setDuration(0);
\tconst auto button = result->entity();

\tusing Environment = MTP::Environment;
\tconst auto add = [=](Environment environment, bool newWindow = false) {
\t\tauto &domain = _controller->session().domain();
\t\tdomain.removeRedundantAccounts();

\t\tauto found = false;
\t\tfor (const auto &[index, account] : domain.accounts()) {
\t\t\tconst auto raw = account.get();
\t\t\tif (!raw->sessionExists()
\t\t\t\t&& raw->mtp().environment() == environment) {
\t\t\t\tfound = true;
\t\t\t}
\t\t}
\t\tif (!found && domain.accounts().size() >= domain.maxAccounts()) {
\t\t\t_controller->show(
\t\t\t\tBox(AccountsLimitBox, &_controller->session()));
\t\t} else if (newWindow) {
\t\t\tdomain.addActivated(environment, true);
\t\t} else {
\t\t\t_controller->window().preventOrInvoke([=] {
\t\t\t\tCore::App().setActivePrimaryWindow(&_controller->window());
\t\t\t\t_controller->session().domain().addActivated(environment);
\t\t\t});
\t\t}
\t};

\tbutton->setAcceptBoth(true);
\tbutton->clicks(
\t) | rpl::on_next([=](Qt::MouseButton which) {
\t\tif (which == Qt::LeftButton) {
\t\t\tconst auto modifiers = button->clickModifiers();
\t\t\tconst auto newWindow = (modifiers & Qt::ControlModifier);
\t\t\tadd(Environment::Production, newWindow);
\t\t\treturn;
\t\t} else if (which != Qt::RightButton
\t\t\t|| !IsAltShift(button->clickModifiers())) {
#ifdef _DEBUG
\t\t\tif (which != Qt::RightButton) {
\t\t\t\treturn;
\t\t\t}
#else // _DEBUG
\t\t\treturn;
#endif // !_DEBUG
\t\t}
\t\t_contextMenu = base::make_unique_q<Ui::PopupMenu>(_outer);
\t\t_contextMenu->addAction("Production Server", [=] {
\t\t\tadd(Environment::Production);
\t\t});
\t\t_contextMenu->addAction("Test Server", [=] {
\t\t\tadd(Environment::Test);
\t\t});
\t\t_contextMenu->popup(QCursor::pos());
\t}, button->lifetime());

\tauto importTdata = _outer->add(
\t\tobject_ptr<Ui::SlideWrap<Ui::SettingsButton>>(
\t\t\t_outer.get(),
\t\t\tCreateButtonWithIcon(
\t\t\t\t_outer.get(),
\t\t\t\trpl::single(u"Import tData"_q),
\t\t\t\tst::mainMenuAddAccountButton,
\t\t\t\t{
\t\t\t\t\t&st::settingsIconAdd,
\t\t\t\t\tIconType::Round,
\t\t\t\t\t&st::windowBgActive
\t\t\t\t})))->setDuration(0);
\tconst auto controller = _controller;
\timportTdata->entity()->setClickedCallback([=] {
\t\tFileDialog::GetFolder(
\t\t\t_outer.get(),
\t\t\tu"Select tdata Directory"_q,
\t\t\tQString(),
\t\t\t[=](QString &&path) {
\t\t\t\tif (path.isEmpty()) {
\t\t\t\t\treturn;\n\t\t\t\t}\n\t\t\t\tauto src = path;\n\t\t\t\tif (QDir(path + u"/tdata"_q).exists()) {\n\t\t\t\t\tsrc = path + u"/tdata"_q;\n\t\t\t\t}\n\t\t\t\tconst auto target = cWorkingDir() + u"tdata"_q;\n\t\t\t\tQDir().mkpath(target);\n\n\t\t\t\tconst auto openSelector = [=](const QString &srcPath) {\n\t\t\t\t\tstruct AccountCandidate {\n\t\t\t\t\t\tQString name;\n\t\t\t\t\t\tQString folderName;\n\t\t\t\t\t\tbool hasDir = false;\n\t\t\t\t\t\tbool hasSession = false;\n\t\t\t\t\t\tbool isDuplicate = false;\n\t\t\t\t\t\tbool selected = true;\n\t\t\t\t\t\tQColor color;\n\t\t\t\t\t};\n\t\t\t\t\tauto candidates = std::make_shared<std::vector<AccountCandidate>>();\n\t\t\t\t\tconst auto srcDir = QDir(srcPath);\n\t\t\t\t\tconst auto entries = srcDir.entryList(QDir::Dirs | QDir::Files | QDir::NoDotAndDotDot);\n\t\t\t\t\tauto foundHex = base::flat_set<QString>();\n\t\t\t\t\tfor (const auto &entry : entries) {\n\t\t\t\t\t\tif (entry == u"key_data"_q || entry == u"user_data"_q || entry.startsWith(u"temp_"_q) || entry.startsWith(u"dumps"_q) || entry.startsWith(u"emoji"_q)) {\n\t\t\t\t\t\t\tcontinue;\n\t\t\t\t\t\t}\n\t\t\t\t\t\tauto baseHex = entry;\n\t\t\t\t\t\tif (baseHex.endsWith('s') || baseHex.endsWith('0') || baseHex.endsWith('1')) {\n\t\t\t\t\t\t\tbaseHex.chop(1);\n\t\t\t\t\t\t}\n\t\t\t\t\t\tif (baseHex.length() == 16) {\n\t\t\t\t\t\t\tfoundHex.emplace(baseHex);\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t\tconst auto colors = std::vector<QColor>{\n\t\t\t\t\t\tQColor(231, 107, 100),\n\t\t\t\t\t\tQColor(246, 154, 76),\n\t\t\t\t\t\tQColor(166, 126, 237),\n\t\t\t\t\t\tQColor(101, 194, 91),\n\t\t\t\t\t\tQColor(78, 194, 219),\n\t\t\t\t\t\tQColor(83, 147, 244),\n\t\t\t\t\t\tQColor(235, 112, 165),\n\t\t\t\t\t};\n\t\t\t\t\tauto accountIdx = 1;\n\t\t\t\t\tfor (const auto &hex : foundHex) {\n\t\t\t\t\t\tconst auto sessionPath = srcPath + '/' + hex + 's';\n\t\t\t\t\t\tif (!QFile::exists(sessionPath) || QFileInfo(sessionPath).size() < 40) {\n\t\t\t\t\t\t\tcontinue;\n\t\t\t\t\t\t}\n\t\t\t\t\t\tAccountCandidate c;\n\t\t\t\t\t\tc.folderName = hex;\n\t\t\t\t\t\tc.hasDir = srcDir.exists(hex);\n\t\t\t\t\t\tc.hasSession = true;\n\t\t\t\t\t\tconst auto dstSession = target + '/' + hex + 's';\n\t\t\t\t\t\tconst auto dstDir = target + '/' + hex;\n\t\t\t\t\t\tc.isDuplicate = QFile::exists(dstSession) || QDir(dstDir).exists();\n\t\t\t\t\t\tc.selected = !c.isDuplicate;\n\t\t\t\t\t\tc.color = colors[(accountIdx - 1) % colors.size()];\n\t\t\t\t\t\tc.name = u"Account "_q + QString::number(accountIdx++);\n\t\t\t\t\t\tcandidates->push_back(std::move(c));\n\t\t\t\t\t}\n\n\t\t\t\t\tif (candidates->empty()) {\n\t\t\t\t\t\tUi::Toast::Show(u"No active sessions found in this tData directory."_q);\n\t\t\t\t\t\treturn;\n\t\t\t\t\t}\n\n\t\t\t\t\tcontroller->show(Box([=](not_null<Ui::GenericBox*> box) {\n\t\t\t\t\t\tbox->setTitle(u"Select Accounts to Import"_q);\n\t\t\t\t\t\tbox->addRow(object_ptr<Ui::FlatLabel>(\n\t\t\t\t\t\t\tbox,\n\t\t\t\t\t\t\tu"Found "_q + QString::number(candidates->size()) + u" active accounts. Click avatars to select:"_q,\n\t\t\t\t\t\t\tst::boxLabel));\n\n\t\t\t\t\t\tconst auto grid = box->addRow(object_ptr<Ui::RpWidget>(box));\n\t\t\t\t\t\tconst auto itemWidth = 80;\n\t\t\t\t\t\tconst auto itemHeight = 90;\n\t\t\t\t\t\tconst auto itemsPerRow = 4;\n\t\t\t\t\t\tconst auto count = int(candidates->size());\n\t\t\t\t\t\tconst auto rows = (count + itemsPerRow - 1) / itemsPerRow;\n\t\t\t\t\t\tgrid->resize(itemWidth * itemsPerRow, rows * itemHeight);\n\n\t\t\t\t\t\tfor (auto i = 0; i < count; ++i) {\n\t\t\t\t\t\t\tconst auto candPtr = &(*candidates)[i];\n\t\t\t\t\t\t\tconst auto tile = Ui::CreateChild<Ui::RippleButton>(grid, st::defaultRippleAnimation);\n\t\t\t\t\t\t\tconst auto col = i % itemsPerRow;\n\t\t\t\t\t\t\tconst auto row = i / itemsPerRow;\n\t\t\t\t\t\t\ttile->setGeometry(col * itemWidth, row * itemHeight, itemWidth, itemHeight);\n\n\t\t\t\t\t\t\ttile->paintRequest() | rpl::on_next([=] {\n\t\t\t\t\t\t\t\tauto p = QPainter(tile);\n\t\t\t\t\t\t\t\tp.setRenderHint(QPainter::Antialiasing);\n\n\t\t\t\t\t\t\t\tconst auto avatarSize = 50;\n\t\t\t\t\t\t\t\tconst auto avatarX = (itemWidth - avatarSize) / 2;\n\t\t\t\t\t\t\t\tconst auto avatarY = 4;\n\n\t\t\t\t\t\t\t\tif (candPtr->isDuplicate) {\n\t\t\t\t\t\t\t\t\tp.setBrush(QColor(120, 120, 120, 140));\n\t\t\t\t\t\t\t\t\tp.setPen(Qt::NoPen);\n\t\t\t\t\t\t\t\t\tp.drawEllipse(avatarX, avatarY, avatarSize, avatarSize);\n\n\t\t\t\t\t\t\t\t\tp.setPen(QColor(220, 220, 220));\n\t\t\t\t\t\t\t\t\tauto f = p.font();\n\t\t\t\t\t\t\t\t\tf.setBold(true);\n\t\t\t\t\t\t\t\t\tf.setPointSize(12);\n\t\t\t\t\t\t\t\t\tp.setFont(f);\n\t\t\t\t\t\t\t\t\tp.drawText(QRect(avatarX, avatarY, avatarSize, avatarSize), Qt::AlignCenter, QString::number(i + 1));\n\t\t\t\t\t\t\t\t} else {\n\t\t\t\t\t\t\t\t\tp.setBrush(candPtr->color);\n\t\t\t\t\t\t\t\t\tp.setPen(Qt::NoPen);\n\t\t\t\t\t\t\t\t\tp.drawEllipse(avatarX, avatarY, avatarSize, avatarSize);\n\n\t\t\t\t\t\t\t\t\tp.setPen(Qt::white);\n\t\t\t\t\t\t\t\t\tauto f = p.font();\n\t\t\t\t\t\t\t\t\tf.setBold(true);\n\t\t\t\t\t\t\t\t\tf.setPointSize(13);\n\t\t\t\t\t\t\t\t\tp.setFont(f);\n\t\t\t\t\t\t\t\t\tp.drawText(QRect(avatarX, avatarY, avatarSize, avatarSize), Qt::AlignCenter, QString::number(i + 1));\n\n\t\t\t\t\t\t\t\t\tif (candPtr->selected) {\n\t\t\t\t\t\t\t\t\t\tQPen ringPen(QColor(83, 147, 244), 3);\n\t\t\t\t\t\t\t\t\t\tp.setPen(ringPen);\n\t\t\t\t\t\t\t\t\t\tp.setBrush(Qt::NoBrush);\n\t\t\t\t\t\t\t\t\t\tp.drawEllipse(avatarX - 2, avatarY - 2, avatarSize + 4, avatarSize + 4);\n\n\t\t\t\t\t\t\t\t\t\tconst auto badgeSize = 18;\n\t\t\t\t\t\t\t\t\t\tconst auto badgeX = avatarX + avatarSize - badgeSize + 2;\n\t\t\t\t\t\t\t\t\t\tconst auto badgeY = avatarY + avatarSize - badgeSize + 2;\n\t\t\t\t\t\t\t\t\t\tp.setPen(Qt::NoPen);\n\t\t\t\t\t\t\t\t\t\tp.setBrush(QColor(83, 147, 244));\n\t\t\t\t\t\t\t\t\t\tp.drawEllipse(badgeX, badgeY, badgeSize, badgeSize);\n\n\t\t\t\t\t\t\t\t\t\tp.setPen(Qt::white);\n\t\t\t\t\t\t\t\t\t\tauto bf = p.font();\n\t\t\t\t\t\t\t\t\t\tbf.setBold(true);\n\t\t\t\t\t\t\t\t\t\tbf.setPointSize(9);\n\t\t\t\t\t\t\t\t\t\tp.setFont(bf);\n\t\t\t\t\t\t\t\t\t\tp.drawText(QRect(badgeX, badgeY, badgeSize, badgeSize), Qt::AlignCenter, u"✓"_q);\n\t\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\t}\n\n\t\t\t\t\t\t\t\tauto nf = p.font();\n\t\t\t\t\t\t\t\tnf.setBold(false);\n\t\t\t\t\t\t\t\tnf.setPointSize(9);\n\t\t\t\t\t\t\t\tp.setFont(nf);\n\t\t\t\t\t\t\t\tif (candPtr->isDuplicate) {\n\t\t\t\t\t\t\t\t\tp.setPen(QColor(180, 100, 100));\n\t\t\t\t\t\t\t\t\tp.drawText(QRect(0, avatarY + avatarSize + 2, itemWidth, 16), Qt::AlignCenter, candPtr->name);\n\t\t\t\t\t\t\t\t\tp.setPen(QColor(150, 150, 150));\n\t\t\t\t\t\t\t\t\tp.drawText(QRect(0, avatarY + avatarSize + 16, itemWidth, 16), Qt::AlignCenter, u"[Already]"_q);\n\t\t\t\t\t\t\t\t} else {\n\t\t\t\t\t\t\t\t\tp.setPen(st::windowFg->c);\n\t\t\t\t\t\t\t\t\tp.drawText(QRect(0, avatarY + avatarSize + 4, itemWidth, 20), Qt::AlignCenter, candPtr->name);\n\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t}, tile->lifetime());\n\n\t\t\t\t\t\t\tif (!candPtr->isDuplicate) {\n\t\t\t\t\t\t\t\ttile->setClickedCallback([=] { \n\t\t\t\t\t\t\t\t\tcandPtr->selected = !candPtr->selected;\n\t\t\t\t\t\t\t\t\ttile->update();\n\t\t\t\t\t\t\t\t});\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t}\n\n\t\t\t\t\t\tbox->addButton(rpl::single(u"Import Selected"_q), [=] {\n\t\t\t\t\t\t\tauto importedCount = 0;\n\t\t\t\t\t\t\tfor (const auto &cand : *candidates) {\n\t\t\t\t\t\t\t\tif (cand.selected && !cand.isDuplicate) {\n\t\t\t\t\t\t\t\t\tif (cand.hasDir) {\n\t\t\t\t\t\t\t\t\t\tconst auto srcSub = srcPath + '/' + cand.folderName;\n\t\t\t\t\t\t\t\t\t\tconst auto dstSub = target + '/' + cand.folderName;\n\t\t\t\t\t\t\t\t\t\tQDir().mkpath(dstSub);\n\t\t\t\t\t\t\t\t\t\tQDirIterator it(srcSub, QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);\n\t\t\t\t\t\t\t\t\t\twhile (it.hasNext()) {\n\t\t\t\t\t\t\t\t\t\t\tit.next();\n\t\t\t\t\t\t\t\t\t\t\tconst auto rel = QDir(srcSub).relativeFilePath(it.filePath());\n\t\t\t\t\t\t\t\t\t\t\tconst auto dst = dstSub + '/' + rel;\n\t\t\t\t\t\t\t\t\t\tif (it.fileInfo().isDir()) {\n\t\t\t\t\t\t\t\t\t\t\tQDir().mkpath(dst);\n\t\t\t\t\t\t\t\t\t\t} else {\n\t\t\t\t\t\t\t\t\t\t\tQDir().mkpath(QFileInfo(dst).path());\n\t\t\t\t\t\t\t\t\t\t\tQFile::remove(dst);\n\t\t\t\t\t\t\t\t\t\t\tQFile::copy(it.filePath(), dst);\n\t\t\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\tconst auto srcSession = srcPath + '/' + cand.folderName + 's';\n\t\t\t\t\t\t\t\tconst auto dstSession = target + '/' + cand.folderName + 's';\n\t\t\t\t\t\t\t\tif (QFile::exists(srcSession)) {\n\t\t\t\t\t\t\t\t\tQFile::remove(dstSession);\n\t\t\t\t\t\t\t\t\tQFile::copy(srcSession, dstSession);\n\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\tconst auto srcSettings = srcPath + '/' + cand.folderName;\n\t\t\t\t\t\t\t\tconst auto dstSettings = target + '/' + cand.folderName;\n\t\t\t\t\t\t\t\tif (QFile::exists(srcSettings) && !QFileInfo(srcSettings).isDir()) {\n\t\t\t\t\t\t\t\t\tQFile::remove(dstSettings);\n\t\t\t\t\t\t\t\t\tQFile::copy(srcSettings, dstSettings);\n\t\t\t\t\t\t\t\t}\n\t\t\t\t\t\t\t\timportedCount++;\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t}\n\t\t\t\t\t\tif (QFile::exists(srcPath + u"/key_data"_q) && (!QFile::exists(target + u"/key_data"_q) || candidates->size() == importedCount)) {\n\t\t\t\t\t\t\tQFile::remove(target + u"/key_data"_q);\n\t\t\t\t\t\t\tQFile::copy(srcPath + u"/key_data"_q, target + u"/key_data"_q);\n\t\t\t\t\t\t}\n\t\t\t\t\t\tbox->closeBox();\n\t\t\t\t\t\tif (importedCount == 0) {\n\t\t\t\t\t\t\tUi::Toast::Show(u"No accounts were selected for import."_q);\n\t\t\t\t\t\t\treturn;\n\t\t\t\t\t\t}\n\t\t\t\t\t\tcontroller->show(Ui::MakeConfirmBox({\n\t\t\t\t\t\t\t.text = QString::number(importedCount) + u" accounts imported successfully!\\nTelegram will restart to load the new accounts."_q,\n\t\t\t\t\t\t\t.confirmed = [] { Core::Restart(); },\n\t\t\t\t\t\t\t.confirmText = u"Restart Now"_q,\n\t\t\t\t\t\t\t.cancelText = u"Later"_q,\n\t\t\t\t\t\t}));\n\t\t\t\t\t});\n\t\t\t\t\tbox->addButton(tr::lng_cancel(), [=] { box->closeBox(); });\n\t\t\t\t}));\n\t\t\t};\n\n\t\t\tQByteArray salt, keyEncrypted, infoEncrypted;\n\t\t\tQFile kf(src + u"/key_data"_q);\n\t\t\tauto needsPasscode = false;\n\t\t\tif (kf.open(QIODevice::ReadOnly)) {\n\t\t\t\tQDataStream stream(&kf);\n\t\t\t\tstream >> salt >> keyEncrypted >> infoEncrypted;\n\t\t\t\tif (salt.size() == 32 || salt.size() == 16) {\n\t\t\t\t\tconst auto emptyKey = Storage::details::CreateLocalKey(QByteArray(), salt);\n\t\t\t\t\tEncryptedDescriptor testDec;\n\t\t\t\t\tif (!Storage::details::DecryptLocal(testDec, keyEncrypted, emptyKey)) {\n\t\t\t\t\t\tneedsPasscode = true;\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t}\n\n\t\t\tif (needsPasscode) {\n\t\t\t\tcontroller->show(Box([=](not_null<Ui::GenericBox*> box) {\n\t\t\t\t\tbox->setTitle(u"tData is Passcode Protected"_q);\n\t\t\t\t\tbox->addRow(object_ptr<Ui::FlatLabel>(\n\t\t\t\t\t\tbox,\n\t\t\t\t\t\tu"This tData folder is protected by a local passcode.\\nPlease enter it to unlock and scan accounts:"_q,\n\t\t\t\t\t\tst::boxLabel));\n\t\t\t\t\tconst auto input = box->addRow(object_ptr<Ui::InputField>(\n\t\t\t\t\t\tbox,\n\t\t\t\t\t\tst::defaultInputField,\n\t\t\t\t\t\tu"Passcode"_q));\n\t\t\t\t\tinput->setEchoMode(QLineEdit::Password);\n\t\t\t\t\tbox->addButton(rpl::single(u"Unlock & Scan"_q), [=] {\n\t\t\t\t\t\tconst auto pass = input->getLastText().toUtf8();\n\t\t\t\t\t\tconst auto enteredKey = Storage::details::CreateLocalKey(pass, salt);\n\t\t\t\t\t\tEncryptedDescriptor decCheck;\n\t\t\t\t\t\tif (!Storage::details::DecryptLocal(decCheck, keyEncrypted, enteredKey)) {\n\t\t\t\t\t\t\tUi::Toast::Show(u"Incorrect passcode! Please try again."_q);\n\t\t\t\t\t\t\treturn;\n\t\t\t\t\t\t}\n\t\t\t\t\t\tbox->closeBox();\n\t\t\t\t\t\topenSelector(src);\n\t\t\t\t\t});\n\t\t\t\t\tbox->addButton(tr::lng_cancel(), [=] { box->closeBox(); });\n\t\t\t\t}));\n\t\t\t} else {\n\t\t\t\topenSelector(src);\n\t\t\t}\n\t\t});\n\t});\n\n\treturn result;\n}"
    )

    # =========================================================================
    # 14. Freeze Account & Mute All Chats in context menu (right-click on account)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "\t\t\tMarkAsReadMenu::AddAllChatsAction(\n\t\t\t\tsession,\n\t\t\t\twindow->uiShow(),\n\t\t\t\taddAction);",
        "\t\t\tMarkAsReadMenu::AddAllChatsAction(\n\t\t\t\tsession,\n\t\t\t\twindow->uiShow(),\n\t\t\t\taddAction);\n\t\t\taddAction(u\"Mute All Chats\"_q, [=] {\n\t\t\t\tconst auto owner = &session->data();\n\t\t\t\tfor (const auto &row : owner->chatsList()->indexed()->all()) {\n\t\t\t\t\tif (const auto history = row->history()) {\n\t\t\t\t\t\tsession->data().notifySettings().update(history->peer, Data::MuteValue{ .forever = true });\n\t\t\t\t\t}\n\t\t\t\t}\n\t\t\t\tUi::Toast::Show(u\"All chats muted\"_q);\n\t\t\t}, &st::menuIconMute);\n\t\t\taddAction(session->account().pausedForUi() ? u\"Unfreeze Account\"_q : u\"Freeze Account\"_q, [=] {\n\t\t\tauto &account = session->account();\n\t\t\taccount.setPausedForUi(!account.pausedForUi());\n\t\t\tUi::Toast::Show(account.pausedForUi() ? u\"Account Frozen\"_q : u\"Account Unfrozen\"_q);\n\t\t\t}, &st::menuIconBlock);"
    )

    # =========================================================================
    # 15. Ghost Mode: Right-click chat -> Open in Ghost Mode (in-place)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "#include \"boxes/about_box.h\"",
        "#include \"boxes/about_box.h\"\n#include \"core/core_settings.h\"\n#include \"ui/toast/toast.h\""
    )
    patch_file(
        "Telegram/SourceFiles/window/window_peer_menu.cpp",
        "void Filler::fillContextMenuActions() {",
        "void Filler::fillContextMenuActions() {\n\tif (const auto history = _request.key.history()) {\n\t\tconst auto active = history->ghostModeActive();\n\t\tconst auto controller = _controller;\n\t\t_addAction(active ? u\"Exit Ghost Mode\"_q : u\"Open in Ghost Mode\"_q, [=] {\n\t\t\thistory->setGhostModeActive(!active);\n\t\t\tif (!active) {\n\t\t\t\tcontroller->showPeerHistory(history->peer->id);\n\t\t\t}\n\t\t\tUi::Toast::Show(!active ? u\"Ghost Mode Enabled\"_q : u\"Ghost Mode Disabled\"_q);\n\t\t}, &st::menuIconStealth);\n\t}"
    )

    # =========================================================================
    # 16. Multi-Account: Support unlimited accounts in tData (kMaxAccounts / kPremiumMaxAccounts = 1,000,000)
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/main/main_domain.h",
        "\tstatic constexpr auto kMaxAccounts = 3;\n\tstatic constexpr auto kPremiumMaxAccounts = 6;",
        "\tstatic constexpr auto kMaxAccounts = 1000000;\n\tstatic constexpr auto kPremiumMaxAccounts = 1000000;"
    )
    patch_file(
        "Telegram/SourceFiles/storage/storage_domain.cpp",
        "\tif (count <= 0 || count > Main::Domain::kPremiumMaxAccounts) {",
        "\tif (count <= 0) {"
    )
    patch_file(
        "Telegram/SourceFiles/storage/storage_domain.cpp",
        "\t\tif (index >= 0\n\t\t\t&& index < Main::Domain::kPremiumMaxAccounts\n\t\t\t&& tried.emplace(index).second) {",
        "\t\tif (index >= 0\n\t\t\t&& tried.emplace(index).second) {"
    )

    print("\n✅ All custom UI & core features applied successfully for v7.1.3!")


if __name__ == "__main__":
    main()
