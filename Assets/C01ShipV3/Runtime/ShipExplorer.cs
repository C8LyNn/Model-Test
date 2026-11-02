using System.Linq;
using UnityEngine;
using UnityEngine.InputSystem;
namespace C01.Ship {
    public class ShipExplorer : MonoBehaviour {
        public GameObject master,roofs,labels;
        public CharacterController player;
        public Camera view;
        public C01Door[] doors;
        public ShipAirlock[] airlocks;
        public bool walking;
        public float walkSpeed=3.5f,flySpeed=14;
        Vector3 overviewPosition;Quaternion overviewRotation;float fallSpeed,overviewSize=26;
        void Start(){overviewPosition=view.transform.position;overviewRotation=view.transform.rotation;overviewSize=view.orthographicSize;player.enabled=false;}
        public void SetWalking(bool value){
            walking=value;player.enabled=value;
            if(value){view.orthographic=false;view.transform.SetParent(player.transform,false);view.transform.localPosition=new Vector3(0,1.6f,0);view.transform.localRotation=Quaternion.identity;roofs.SetActive(true);labels.SetActive(false);}
            else{view.transform.SetParent(null,true);view.transform.SetPositionAndRotation(overviewPosition,overviewRotation);view.orthographic=true;view.orthographicSize=overviewSize;roofs.SetActive(false);labels.SetActive(true);}
        }
        public void Interact(C01Door door){
            var airlock=airlocks.FirstOrDefault(a=>a.doorA==door||a.doorB==door);
            if(airlock!=null)airlock.Request(door,!door.IsOpen);else door.Toggle();
        }
        void SetOrdinaryDoors(bool open){foreach(var d in doors)if(!airlocks.Any(a=>a.doorA==d||a.doorB==d))d.SetOpen(open);}
        void Update(){
            var k=Keyboard.current;var mouse=Mouse.current;if(k==null)return;
            if(k.digit1Key.wasPressedThisFrame)SetWalking(false);if(k.digit2Key.wasPressedThisFrame)SetWalking(true);
            if(k.rKey.wasPressedThisFrame)roofs.SetActive(!roofs.activeSelf);if(k.lKey.wasPressedThisFrame)labels.SetActive(!labels.activeSelf);
            if(k.oKey.wasPressedThisFrame)SetOrdinaryDoors(true);if(k.kKey.wasPressedThisFrame)SetOrdinaryDoors(false);
            if(k.eKey.wasPressedThisFrame&&Physics.Raycast(view.transform.position,view.transform.forward,out var hit,3.5f)){
                var d=hit.collider.GetComponentInParent<C01Door>();if(d!=null)Interact(d);
            }
            bool look=mouse!=null&&mouse.rightButton.isPressed;var delta=look?mouse.delta.ReadValue()*.12f:Vector2.zero;
            var move=new Vector3((k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0),0,(k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0));
            if(walking){
                player.transform.Rotate(0,delta.x,0);var e=view.transform.localEulerAngles;float pitch=e.x>180?e.x-360:e.x;view.transform.localRotation=Quaternion.Euler(Mathf.Clamp(pitch-delta.y,-80,80),0,0);
                fallSpeed=player.isGrounded?-1:fallSpeed-15*Time.deltaTime;player.Move((player.transform.TransformDirection(move.normalized)*walkSpeed+Vector3.up*fallSpeed)*Time.deltaTime);
            }else if(look){
                view.orthographic=false;var e=view.transform.eulerAngles;view.transform.rotation=Quaternion.Euler(e.x-delta.y,e.y+delta.x,0);
                move.y=(k.qKey.isPressed?1:0)-(k.zKey.isPressed?1:0);view.transform.position+=view.transform.TransformDirection(move)*flySpeed*Time.deltaTime;
            }
        }
        void OnGUI(){
            GUILayout.BeginArea(new Rect(14,14,310,175),GUI.skin.box);GUILayout.Label("C01 / STATEK - PLAN POKLADU");
            if(GUILayout.Button(walking?"1  Widok calego statku":"2  Spacer po statku"))SetWalking(!walking);
            if(GUILayout.Button("R  Pokaz / ukryj sufit"))roofs.SetActive(!roofs.activeSelf);
            GUILayout.Label("WASD + prawy przycisk myszy | E: drzwi");GUILayout.Label("O / K: otworz / zamknij drzwi wewnetrzne");GUILayout.Label("L: etykiety | sluzy zamykaja drugie drzwi");GUILayout.EndArea();
            if(walking)GUI.Label(new Rect(Screen.width/2-4,Screen.height/2-9,20,20),"+");
        }
    }
}
