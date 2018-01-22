:: Script to commit and push all changes to Github
:: WARNING: This will overwrite any existing changes on remote
@ECHO OFF
SETLOCAL ENABLEEXTENSIONS
SET script_name=%~n0
SET script_parent_folder=%~dp0

SET commit_msg=%~n1

IF "%commit_msg%"=="" (
	ECHO ERROR: No commit message was passed as argument
	EXIT /B 1
)

ECHO Starting commit and push of file(s) to GitHub...

git add .
git status

IF /I "%ERRORLEVEL%" NEQ "0" (
	ECHO "Unable to execute Git command"
	EXIT /B 1
)

SET /P confirm="Continue with push command [y/n]>"

IF "%confirm%"=="y" (

git commit -m "%commit_msg%"

IF /I "%ERRORLEVEL%" NEQ "0" (
	ECHO "ERROR: while commiting changes to repository!"
	EXIT /B 1
)

git push

IF /I "%ERRORLEVEL%" NEQ "0" (
	ECHO "ERROR: while pushing files to remote!"
	EXIT /B 1
)

ECHO "File(s) pushed to github successfully!"
) else (
ECHO "File(s) push cancelled!"
)