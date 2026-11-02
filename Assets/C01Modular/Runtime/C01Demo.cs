using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif
namespace C01 {
    public class C01Demo : MonoBehaviour {
        public GameObject master;
        public C01Door[] doors;
        public float moveSpeed=5;
        void OnGUI() {
            GUILayout.BeginArea(new Rect(12,12,270,210),GUI.skin.box);
            GUILayout.Label("C01 PASS 02 - 3 rooms / 3 doors");
            foreach(var d in doors) if(d!=null && GUILayout.Button(d.name+" : "+(d.IsOpen?"close":"open"))) d.Toggle();
            if(GUILayout.Button("Toggle ceilings")) ToggleCeilings();
            GUILayout.Label("RMB + WASD/QZ: fly | E: aimed door");
            GUILayout.EndArea();
        }
        void ToggleCeilings() {
            foreach(var m in master.GetComponentsInChildren<C01Module>(true)) if(m.family=="ceiling")m.gameObject.SetActive(!m.gameObject.activeSelf);
        }
        void Update() {
            Vector3 move=Vector3.zero;Vector2 mouse=Vector2.zero;bool look=false,interact=false;
#if ENABLE_INPUT_SYSTEM
            var k=Keyboard.current;var m=Mouse.current;
            if(k!=null){move=new Vector3((k.dKey.isPressed?1:0)-(k.aKey.isPressed?1:0),(k.qKey.isPressed?1:0)-(k.zKey.isPressed?1:0),(k.wKey.isPressed?1:0)-(k.sKey.isPressed?1:0));interact=k.eKey.wasPressedThisFrame;}
            if(m!=null){look=m.rightButton.isPressed;mouse=m.delta.ReadValue()*.12f;}
#else
            move=new Vector3(Input.GetAxisRaw("Horizontal"),(Input.GetKey(KeyCode.Q)?1:0)-(Input.GetKey(KeyCode.Z)?1:0),Input.GetAxisRaw("Vertical"));
            look=Input.GetMouseButton(1);mouse=new Vector2(Input.GetAxis("Mouse X"),Input.GetAxis("Mouse Y"))*2;interact=Input.GetKeyDown(KeyCode.E);
#endif
            if(look){transform.position+=transform.TransformDirection(move)*moveSpeed*Time.deltaTime;var e=transform.eulerAngles;transform.rotation=Quaternion.Euler(e.x-mouse.y,e.y+mouse.x,0);}
            if(interact && Physics.Raycast(transform.position,transform.forward,out var hit,4)) {
                var door=hit.collider.GetComponentInParent<C01Door>();if(door!=null)door.Toggle();
            }
        }
    }
}
