'use client';
import {createContext, useContext, useState, type Dispatch, type SetStateAction, type ReactNode} from 'react';
import type {ExperimentDraft} from '../lib/experiment-file';
type Session = {draft: ExperimentDraft; setDraft: Dispatch<SetStateAction<ExperimentDraft>>; archive: unknown[]; setArchive: Dispatch<SetStateAction<unknown[]>>};
const SessionContext = createContext<Session | null>(null);
export function ExperimentSession({children}: {children: ReactNode}) {
 const [draft,setDraft]=useState<ExperimentDraft>({context:{body_revision:'',glaze_revision:'',application_revision:'',firing_run_id:'',specimen_id:'',sensor_location:''},rows:[{time:'',predicted:'',observed:''},{time:'',predicted:'',observed:''}],source:'',model:'',kind:'REAL'});
 const [archive,setArchive]=useState<unknown[]>([]);
 return <SessionContext.Provider value={{draft,setDraft,archive,setArchive}}>{children}</SessionContext.Provider>;
}
export function useExperimentSession(){const session=useContext(SessionContext);if(!session)throw new Error('ExperimentSession missing');return session;}
