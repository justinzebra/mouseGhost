import subprocess

def switch_chrome_tab():
    """
    隨機切換 Google Chrome 前景視窗中的一個分頁
    若只有 1 個分頁則不動作
    """
    script = '''
    tell application "Google Chrome"
        if (count of windows) = 0 then return
        set w to front window
        set tabCount to count of tabs of w
        if tabCount > 1 then
            set newIndex to (random number from 1 to tabCount)
            set active tab index of w to newIndex
        end if
    end tell
    '''
    subprocess.run(["osascript", "-e", script],
                   stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)
