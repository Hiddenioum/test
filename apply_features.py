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
        "\t[[nodiscard]] bool locallyDeleted() const {\n\t\treturn _locallyDeleted;\n\t}\n\tvoid setLocallyDeleted(bool deleted);\n\ttoggleOriginalEditVersion();\n\n\t[[nodiscard]] bool out() const {"
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
    # 13. Import tData: Smart account picker + duplicate filter + 1-click Restart Box
    # =========================================================================
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "#include \"settings/sections/settings_information.h\"",
        "#include \"settings/sections/settings_information.h\"\n#include \"core/file_utilities.h\"\n#include \"core/application.h\"\n#include \"ui/toast/toast.h\"\n#include \"ui/boxes/confirm_box.h\"\n#include \"ui/widgets/checkbox.h\"\n#include \"ui/widgets/labels.h\"\n#include \"boxes/abstract_box.h\"\n#include \"history/history.h\"\n#include \"data/notify/data_notify_settings.h\"\n#include \"data/notify/data_peer_notify_settings.h\"\n#include <QDir>\n#include <QFile>\n#include <QDirIterator>"
    )
    patch_file(
        "Telegram/SourceFiles/settings/sections/settings_information.cpp",
        "not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {",
        'not_null<Ui::SlideWrap<Ui::SettingsButton>*> AccountsList::setupAdd() {\n'
        '\tauto importTdata = _outer->add(\n'
        '\t\tobject_ptr<Ui::SlideWrap<Ui::SettingsButton>>(\n'
        '\t\t\t_outer.get(),\n'
        '\t\t\tCreateButtonWithIcon(\n'
        '\t\t\t\t_outer.get(),\n'
        '\t\t\t\trpl::single(u"Import tData"_q),\n'
        '\t\t\t\tst::mainMenuAddAccountButton,\n'
        '\t\t\t\t{\n'
        '\t\t\t\t\t&st::settingsIconAdd,\n'
        '\t\t\t\t\tIconType::Round,\n'
        '\t\t\t\t\t&st::windowBgActive\n'
        '\t\t\t\t})))->setDuration(0);\n'
        '\tconst auto controller = _controller;\n'
        '\timportTdata->entity()->setClickedCallback([=] {\n'
        '\t\tFileDialog::GetFolder(\n'
        '\t\t\t_outer.get(),\n'
        '\t\t\tu"Select tdata Directory"_q,\n'
        '\t\t\tQString(),\n'
        '\t\t\t[=](QString &&path) {\n'
        '\t\t\t\tif (path.isEmpty()) {\n'
        '\t\t\t\t\treturn;\n'
        '\t\t\t\t}\n'
        '\t\t\t\tauto src = path;\n'
        '\t\t\t\tif (QDir(path + u"/tdata"_q).exists()) {\n'
        '\t\t\t\t\tsrc = path + u"/tdata"_q;\n'
        '\t\t\t\t}\n'
        '\t\t\t\tconst auto target = cWorkingDir() + u"tdata"_q;\n'
        '\t\t\t\tQDir().mkpath(target);\n'
        '\n'
        '\t\t\t\tstruct AccountCandidate {\n'
        '\t\t\t\t\tQString name;\n'
        '\t\t\t\t\tQString folderName;\n'
        '\t\t\t\t\tbool hasDir = false;\n'
        '\t\t\t\t\tbool hasSession = false;\n'
        '\t\t\t\t\tbool isDuplicate = false;\n'
        '\t\t\t\t\tUi::Checkbox *checkbox = nullptr;\n'
        '\t\t\t\t};\n'
        '\t\t\t\tauto candidates = std::make_shared<std::vector<AccountCandidate>>();\n'
        '\t\t\t\tconst auto srcDir = QDir(src);\n'
        '\t\t\t\tconst auto entries = srcDir.entryList(QDir::Dirs | QDir::Files | QDir::NoDotAndDotDot);\n'
        '\t\t\t\tauto foundHex = base::flat_set<QString>();\n'
        '\t\t\t\tfor (const auto &entry : entries) {\n'
        '\t\t\t\t\tif (entry == u"key_data"_q || entry == u"user_data"_q || entry.startsWith(u"temp_"_q) || entry.startsWith(u"dumps"_q) || entry.startsWith(u"emoji"_q)) {\n'
        '\t\t\t\t\t\tcontinue;\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t\tauto baseHex = entry;\n'
        '\t\t\t\t\tif (baseHex.endsWith(\'s\') || baseHex.endsWith(\'0\') || baseHex.endsWith(\'1\')) {\n'
        '\t\t\t\t\t\tbaseHex.chop(1);\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t\tif (baseHex.length() == 16) {\n'
        '\t\t\t\t\t\tfoundHex.emplace(baseHex);\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t\tauto accountIdx = 1;\n'
        '\t\t\t\t\tfor (const auto &hex : foundHex) {\n'
        '\t\t\t\t\tAccountCandidate c;\n'
        '\t\t\t\t\tc.folderName = hex;\n'
        '\t\t\t\t\tc.hasDir = srcDir.exists(hex);\n'
        '\t\t\t\t\tc.hasSession = QFile::exists(src + \'/\' + hex + \'s\');\n'
        '\t\t\t\t\tconst auto dstSession = target + \'/\' + hex + \'s\';\n'
        '\t\t\t\t\tconst auto dstDir = target + \'/\' + hex;\n'
        '\t\t\t\t\tc.isDuplicate = QFile::exists(dstSession) || QDir(dstDir).exists();\n'
        '\t\t\t\t\tc.name = u"Account "_q + QString::number(accountIdx++) + u" ("_q + hex + u")"_q;\n'
        '\t\t\t\t\tcandidates->push_back(std::move(c));\n'
        '\t\t\t\t}\n'
        '\n'
        '\t\t\t\tif (candidates->empty()) {\n'
        '\t\t\t\t\tQDirIterator it(src, QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);\n'
        '\t\t\t\t\twhile (it.hasNext()) {\n'
        '\t\t\t\t\t\tit.next();\n'
        '\t\t\t\t\t\tconst auto rel = QDir(src).relativeFilePath(it.filePath());\n'
        '\t\t\t\t\t\tconst auto dst = target + \'/\' + rel;\n'
        '\t\t\t\t\t\tif (it.fileInfo().isDir()) {\n'
        '\t\t\t\t\t\t\tQDir().mkpath(dst);\n'
        '\t\t\t\t\t\t} else {\n'
        '\t\t\t\t\t\t\tQDir().mkpath(QFileInfo(dst).path());\n'
        '\t\t\t\t\t\t\tQFile::remove(dst);\n'
        '\t\t\t\t\t\t\tQFile::copy(it.filePath(), dst);\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t\tcontroller->show(Ui::MakeConfirmBox({\n'
        '\t\t\t\t\t\t.text = u"tData files imported!\\nTelegram needs to restart to load the sessions."_q,\n'
        '\t\t\t\t\t\t.confirmed = [] { Core::Restart(); },\n'
        '\t\t\t\t\t\t.confirmText = u"Restart Now"_q,\n'
        '\t\t\t\t\t\t.cancelText = u"Later"_q,\n'
        '\t\t\t\t\t}));\n'
        '\t\t\t\t\treturn;\n'
        '\t\t\t\t}\n'
        '\n'
        '\t\t\t\tcontroller->show(Box([=](not_null<Ui::GenericBox*> box) {\n'
        '\t\t\t\t\tbox->setTitle(u"Select tData Accounts to Import"_q);\n'
        '\t\t\t\t\tbox->addRow(object_ptr<Ui::FlatLabel>(\n'
        '\t\t\t\t\t\tbox,\n'
        '\t\t\t\t\t\tu"Found "_q + QString::number(candidates->size()) + u" accounts. Duplicates are auto-unselected:"_q,\n'
        '\t\t\t\t\t\tst::boxLabel));\n'
        '\t\t\t\t\tfor (auto &cand : *candidates) {\n'
        '\t\t\t\t\t\tconst auto labelText = cand.name + (cand.isDuplicate ? u" [Already in Telegram]"_q : QString());\n'
        '\t\t\t\t\t\tconst auto isChecked = !cand.isDuplicate;\n'
        '\t\t\t\t\t\tcand.checkbox = box->addRow(object_ptr<Ui::Checkbox>(\n'
        '\t\t\t\t\t\t\tbox,\n'
        '\t\t\t\t\t\t\tlabelText,\n'
        '\t\t\t\t\t\t\tisChecked));\n'
        '\t\t\t\t\t}\n'
        '\t\t\t\t\tbox->addButton(rpl::single(u"Import Selected"_q), [=] {\n'
        '\t\t\t\t\t\tauto importedCount = 0;\n'
        '\t\t\t\t\t\tfor (const auto &cand : *candidates) {\n'
        '\t\t\t\t\t\t\tif (cand.checkbox && cand.checkbox->checked()) {\n'
        '\t\t\t\t\t\t\t\tif (cand.hasDir) {\n'
        '\t\t\t\t\t\t\t\t\tconst auto srcSub = src + \'/\' + cand.folderName;\n'
        '\t\t\t\t\t\t\t\t\tconst auto dstSub = target + \'/\' + cand.folderName;\n'
        '\t\t\t\t\t\t\t\t\tQDir().mkpath(dstSub);\n'
        '\t\t\t\t\t\t\t\t\tQDirIterator it(srcSub, QDir::Files | QDir::Dirs | QDir::NoDotAndDotDot, QDirIterator::Subdirectories);\n'
        '\t\t\t\t\t\t\t\t\twhile (it.hasNext()) {\n'
        '\t\t\t\t\t\t\t\t\t\tit.next();\n'
        '\t\t\t\t\t\t\t\t\t\tconst auto rel = QDir(srcSub).relativeFilePath(it.filePath());\n'
        '\t\t\t\t\t\t\t\t\t\tconst auto dst = dstSub + \'/\' + rel;\n'
        '\t\t\t\t\t\t\t\t\t\tif (it.fileInfo().isDir()) {\n'
        '\t\t\t\t\t\t\t\t\t\t\tQDir().mkpath(dst);\n'
        '\t\t\t\t\t\t\t\t\t\t} else {\n'
        '\t\t\t\t\t\t\t\t\t\t\tQDir().mkpath(QFileInfo(dst).path());\n'
        '\t\t\t\t\t\t\t\t\t\t\tQFile::remove(dst);\n'
        '\t\t\t\t\t\t\t\t\t\t\tQFile::copy(it.filePath(), dst);\n'
        '\t\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\tconst auto srcSession = src + \'/\' + cand.folderName + \'s\';\n'
        '\t\t\t\t\t\t\t\tconst auto dstSession = target + \'/\' + cand.folderName + \'s\';\n'
        '\t\t\t\t\t\t\t\tif (QFile::exists(srcSession)) {\n'
        '\t\t\t\t\t\t\t\t\tQFile::remove(dstSession);\n'
        '\t\t\t\t\t\t\t\t\tQFile::copy(srcSession, dstSession);\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\tconst auto srcSettings = src + \'/\' + cand.folderName;\n'
        '\t\t\t\t\t\t\t\tconst auto dstSettings = target + \'/\' + cand.folderName;\n'
        '\t\t\t\t\t\t\t\tif (QFile::exists(srcSettings) && !QFileInfo(srcSettings).isDir()) {\n'
        '\t\t\t\t\t\t\t\t\tQFile::remove(dstSettings);\n'
        '\t\t\t\t\t\t\t\t\tQFile::copy(srcSettings, dstSettings);\n'
        '\t\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t\t\timportedCount++;\n'
        '\t\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\tif (QFile::exists(src + u"/key_data"_q) && (!QFile::exists(target + u"/key_data"_q) || candidates->size() == importedCount)) {\n'
        '\t\t\t\t\t\t\tQFile::remove(target + u"/key_data"_q);\n'
        '\t\t\t\t\t\t\tQFile::copy(src + u"/key_data"_q, target + u"/key_data"_q);\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\tbox->closeBox();\n'
        '\t\t\t\t\t\tif (importedCount == 0) {\n'
        '\t\t\t\t\t\t\tUi::Toast::Show(u"No accounts were selected for import."_q);\n'
        '\t\t\t\t\t\t\treturn;\n'
        '\t\t\t\t\t\t}\n'
        '\t\t\t\t\t\tcontroller->show(Ui::MakeConfirmBox({\n'
        '\t\t\t\t\t\t\t.text = QString::number(importedCount) + u" accounts imported successfully!\\nTelegram must restart to load the new accounts."_q,\n'
        '\t\t\t\t\t\t\t.confirmed = [] { Core::Restart(); },\n'
        '\t\t\t\t\t\t\t.confirmText = u"Restart Now"_q,\n'
        '\t\t\t\t\t\t\t.cancelText = u"Later"_q,\n'
        '\t\t\t\t\t\t}));\n'
        '\t\t\t\t\t});\n'
        '\t\t\t\t\tbox->addButton(tr::lng_cancel(), [=] { box->closeBox(); });\n'
        '\t\t\t\t}));\n'
        '\t\t\t});\n'
        '\t});'
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
