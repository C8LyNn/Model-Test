"""Editable bridge layout in metres; all models come from the v6.8 kit."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def build():
    stations = [
        # Front flight pair and their chairs.
        ('BRIDGE_HELM_STATION','P_V68_CommandConsole',-31,39.6,False),
        ('BRIDGE_NAV_STATION','P_V68_CommandConsole',-31,45.6,False),
        ('BRIDGE_HELM_CHAIR','P_V68_CommandChair',-28.5,39.9,False),
        ('BRIDGE_NAV_CHAIR','P_V68_CommandChair',-28.5,45.9,False),
        ('BRIDGE_CAPTAIN_CHAIR','P_V68_CommandChair',-24,42.9,False),
        # Science and communications flank the command position.
        ('BRIDGE_SCIENCE_STATION','P_V68_CommandConsole',-24,37.2,False),
        ('BRIDGE_COMMS_STATION','P_V68_CommandConsole',-24,48,False),
        ('BRIDGE_SCIENCE_CHAIR','P_V68_CommandChair',-21.5,37.5,True),
        ('BRIDGE_COMMS_CHAIR','P_V68_CommandChair',-21.5,48.3,True),
        # Rear tactical and engineering pair, set clear of the central route.
        ('BRIDGE_TACTICAL_STATION','P_V68_CommandConsole',-18,38.7,True),
        ('BRIDGE_ENGINEERING_STATION','P_V68_CommandConsole',-18,46.5,True),
        ('BRIDGE_TACTICAL_CHAIR','P_V68_CommandChair',-15.5,39,True),
        ('BRIDGE_ENGINEERING_CHAIR','P_V68_CommandChair',-15.5,46.8,True),
        # Displays keep the original four-screen forward bank and flank it.
        ('BRIDGE_DISPLAY_0','P_V68_StatusDisplay',-34.5,37.5,False),
        ('BRIDGE_DISPLAY_1','P_V68_StatusDisplay',-34.5,40.5,False),
        ('BRIDGE_DISPLAY_2','P_V68_StatusDisplay',-34.5,43.5,False),
        ('BRIDGE_DISPLAY_3','P_V68_StatusDisplay',-34.5,46.5,False),
        ('BRIDGE_DISPLAY_S','P_V68_StatusDisplay',-34.5,34.6,True),
        ('BRIDGE_DISPLAY_N','P_V68_StatusDisplay',-34.5,49.6,True),
    ]
    return {'version':'C01.SHIP.6.9','grid':3,'symmetryZ':43.5,
            'placements':[{'id':i,'model':model,'x':x,'y':0,'z':z,'yaw':0,'added':added}
                          for i,model,x,z,added in stations]}

if __name__ == '__main__':
    path=ROOT/'Assets/C01ShipV69/Data/bridge_layout.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(build(),indent=2),encoding='utf8')
    print('Wrote',path)
