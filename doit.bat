@echo off
cd /d D:\Projects\SIH\SIH26095
echo --- pre-commit ---
git status --short
echo --- git add -A ---
git add -A
echo --- git status --short ---
git status --short
echo --- git commit ---
git commit -m docs: add planv5 and DEMO_GUIDE
echo --- git log ---
git log --oneline -3
