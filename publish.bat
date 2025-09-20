@echo off
REM ===== GitHub Pages 自動反映バッチ =====
REM 位置: climax2 フォルダ直下に置いて使う

cd /d %~dp0

REM サイトをローカルで生成（プレビュー不要ならこの行はコメントアウト可）
python generate_site.py

REM Git に追加してコミット
git add .
git commit -m "auto: update site (%date% %time%)"

REM main ブランチにプッシュ
git push origin main

echo.
echo [OK] GitHub にプッシュしました。数分後に公開ページが更新されます。
pause
