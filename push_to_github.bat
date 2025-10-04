@echo off
cd /d D:\yt_dlp_backend

echo ================================
echo 🚀 Pushing NTUBE Backend to GitHub...
echo ================================

git init
git remote remove origin
git remote add origin https://github.com/Tanvir0144/ntube-backend.git

git add .
git commit -m "🔄 Auto update: NTUBE Ultra Backend latest changes"
git branch -M main
git push -u origin main --force

echo.
echo ✅ Push completed successfully!
echo 🌐 GitHub Repository: https://github.com/Tanvir0144/ntube-backend
echo.
pause
