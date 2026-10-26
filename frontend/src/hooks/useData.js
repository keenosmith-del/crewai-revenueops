import {useEffect,useState,useCallback} from 'react'
import {api} from '../services/api'
export function useData(path){
  const [data,setData]=useState(null),[error,setError]=useState(''),[loading,setLoading]=useState(true)
  const reload=useCallback(()=>{setLoading(true);setError('');return api(path).then(setData).catch(e=>setError(e.message)).finally(()=>setLoading(false))},[path])
  useEffect(()=>{let active=true;api(path).then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(e.message)}).finally(()=>{if(active)setLoading(false)});return()=>{active=false}},[path])
  return {data,error,loading,reload}
}
