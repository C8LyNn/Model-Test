using UnityEngine;
namespace C01 {
    public class C01Door : MonoBehaviour {
        public Transform hinge;
        [SerializeField, Range(0,90)] float angle;
        [SerializeField, Range(0,90)] float target;
        public float degreesPerSecond=90;
        public float Angle => angle;
        public bool IsOpen => target>45;
        public void SetOpen(bool open) { target=open?90:0; }
        public void Toggle() { SetOpen(!IsOpen); }
        public void SetAngleImmediate(float value) {
            angle=target=Mathf.Clamp(value,0,90); Apply();
        }
        void Apply() { if(hinge!=null) hinge.localRotation=Quaternion.Euler(0,angle,0); }
        void Update() { angle=Mathf.MoveTowards(angle,target,degreesPerSecond*Time.deltaTime);Apply(); }
        void OnValidate() { angle=Mathf.Clamp(angle,0,90);target=Mathf.Clamp(target,0,90);Apply(); }
    }
}
