import Button from 'react-bootstrap/Button';

import EditIcon from '@mui/icons-material/Edit';
import MoreVertOutlinedIcon from '@mui/icons-material/MoreVertOutlined';
import BlockIcon from '@mui/icons-material/Block';
import { useRef, useState } from 'react';
import UsersTable from './UsersTable.jsx';

const DashboardDetails = () => {
	const [isAddNew, setIsAddNew] = useState(false);
	

	// filters state
	const [filters, setFilters] = useState({});
	const [checkBoxFilters, setCheckBoxFilter] = useState([]);
	const [startDate, setStartDate] = useState(null);
	const [endDate, setEndDate] = useState(null);
	const formRef = useRef(null);

	const handleClose = () => setIsAddNew(false);

	return (
		<>
			<div className="d-flex justify-content-between mb-3">
				<h3 style={{color:"#fff"}}>User Management</h3>
				<Button variant="success" onClick={(e) => setIsAddNew(true)}>
					Add New
				</Button>
			</div>
			<div className="border">

				<UsersTable
					startDate={startDate}
					endDate={endDate}
					filters={filters}
					checkBoxFilters={checkBoxFilters}
					show={isAddNew}
					handleClose={handleClose}
				/>
			</div>
		</>
	);
};

export default DashboardDetails;
