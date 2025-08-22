
# -*- coding: utf-8 -*-
# 用途：收集近 24h 指標（P95 latency、error rate）並建議模型等級與溫度設定（示意）。
def main():
    print("建議：互動模型=gemini-2.0-flash, 溫度=0.2 ; 高推理場景改用 -pro, 溫度=0.1")
if __name__=='__main__':
    main()
