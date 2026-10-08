import type { Metadata } from 'next';
import LabMeasurements from '../../../components/lab-measurements';
import './measurements.css';

export const metadata: Metadata = { title: 'Numune kayıtları · Ceramic Glaze Lab' };

export default function Page() { return <LabMeasurements />; }
