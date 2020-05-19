#Persistent
#SingleInstance, force

MsgBox, "Noethys AHK reloaded"
Loop
{
	IfWinActive, ahk_exe Noethys.exe
	{
		IfWinActive, Ouverture du fichier [RESEAU]
		{
			Send ^a
			Send 6rZpGZZjrUDyoR2Hh92B
			Sleep, 1000
		}
		IfWinActive, L'offre de services de Noethys
		{
			WinClose, L'offre de services de Noethys
			Sleep, 500
		}
		IfWinActive, Anomalies
		{
			WinClose, Anomalies
			Sleep, 500
		}
		IfWinActive, Réinitialisation
		{
			Send {Enter}
		}
	}
	Sleep, 200
}
