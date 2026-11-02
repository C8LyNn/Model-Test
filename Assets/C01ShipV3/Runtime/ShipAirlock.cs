using System.Collections;
using UnityEngine;
namespace C01.Ship {
    public class ShipAirlock : MonoBehaviour {
        public C01Door doorA,doorB;
        Coroutine sequence;
        public void Request(C01Door requested,bool open){
            if(requested!=doorA&&requested!=doorB)throw new System.ArgumentException("Door does not belong to this airlock");
            if(sequence!=null){StopCoroutine(sequence);sequence=null;}
            if(!open){requested.SetOpen(false);return;}
            sequence=StartCoroutine(OpenAfterClosingOther(requested,requested==doorA?doorB:doorA));
        }
        IEnumerator OpenAfterClosingOther(C01Door wanted,C01Door other){
            other.SetOpen(false);float deadline=Time.time+5;
            while(other.Angle>.01f&&Time.time<deadline)yield return null;
            if(other.Angle<=.01f)wanted.SetOpen(true);
            sequence=null;
        }
        void OnDisable(){if(sequence!=null)StopCoroutine(sequence);sequence=null;}
    }
}
