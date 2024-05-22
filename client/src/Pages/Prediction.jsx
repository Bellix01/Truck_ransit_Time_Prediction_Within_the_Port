import React, { useEffect, useState } from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import copy from 'clipboard-copy';
import './Prediction.css';  

const Prediction = () => {
    const [customers, setCustomers] = useState([]);
    const [globalFilter, setGlobalFilter] = useState("");
    const [copyRowId, setCopyRowId] = useState(null);
    const [showCopiedMessage, setShowCopiedMessage] = useState(false);
    const [value, setValue] = useState("");

    useEffect(() => {
        fetch("http://127.0.0.1:5000/")
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => setCustomers(data))
            .catch(error => console.error("Error fetching data:", error));
    }, []);

    //part of copy button
    const handleCopy = (customerId) => {
        copy(customerId);
        setShowCopiedMessage(true);
 
        setTimeout(() => {
            setShowCopiedMessage(false);
        }, 500);
    };

    const handleRowEnter = (rowData) => {
        setCopyRowId(rowData.CustomerID);
    };
    
    const handleRowLeave = () => {
        setCopyRowId(null);
    };
    
    const renderCopyButton = (rowData) => {
        const isCopyVisible = rowData.CustomerID === copyRowId;
    
        return (
            <div
                onMouseEnter={() => handleRowEnter(rowData)}
                onMouseLeave={handleRowLeave}
                className="copy-button-container"
            >
                <span>{rowData.CustomerID}</span>
                {isCopyVisible && (
                    <>
                    <Button 
                        icon="pi pi-copy"
                        className="copy-icon" 
                        tooltip=""
                        onClick={() => handleCopy(rowData.CustomerID)} 
                    />
                    {showCopiedMessage && <span className="copied-message">Copied</span>}
                </>
                )}
            </div>
        );
    };

//    Part of search and clear
    const clearSearch = () => {
        setGlobalFilter("");
    };
    
    const renderHeader = () => {
        return (
            <div className="flex justify-content-between align-items-center header-container">
                <Button 
                    type="button" 
                    icon="pi pi-filter-slash" 
                    label="Clear" 
                    className="p-button-outlined clear-button"
                    onClick={clearSearch} 
                />
                <span className="p-input-icon-left search-input">
                    <i className="pi pi-search search-icon" />
                    <InputText 
                        type="search"
                        value={globalFilter}
                        onChange={(e) => setGlobalFilter(e.target.value)}
                        placeholder="Keyword Search"
                        className="search-box"
                    />
                </span>
            </div>
        );
    };
    const header = renderHeader();
    
    const footer = <p>Total customers = {customers ? customers.length : 0}</p>;

    return (
        <div className="container">
            <div className="table-wrapper">
              
                {/* <div className="card"> */}
                <DataTable
                    value={customers}
                    paginator
                    removableSort
                    rows={5}
                    scrollable
                    scrolldirection="horizontal"
                    // rowsPerPageOptions={[5, 10, 25, 50]}
                    tableStyle={{ minWidth: '10rem' }}
                    className="custom-table"
                    header={header}
                    globalFilter={globalFilter}
                    footer={footer}
                >
                        <Column field="CustomerID" header="Customer ID" sortable style={{ width: '25%' }} body={renderCopyButton} ></Column>  
                        <Column field="CompanyName" header="Company Name" sortable style={{ width: '25%' }}></Column>
                        <Column field="ContactName" header="Contact Name" sortable style={{ width: '25%' }}></Column>
                        <Column field="ContactTitle" header="Contact Title" sortable style={{ width: '25%' }}></Column>
                        <Column field="Address" header="Address" sortable style={{ width: '25%' }}></Column>
                        <Column field="City" header="City" sortable style={{ width: '25%' }}></Column>
                        <Column field="PostalCode" header="Postal Code" sortable style={{ width: '25%' }}></Column>
                        <Column field="Country" header="Country" sortable style={{ width: '25%' }}></Column>
                        <Column field="Phone" header="Phone" sortable style={{ width: '25%' }}></Column>
                </DataTable>
                {/* </div> */}
            </div>
            <div className="predict-section">
                <div className="sub-section left-div">
                    <h2 className="">Truck Transit Time</h2>
                    <h5>Enter the AMP_ID to get the specific truck informations.</h5>
                    <span className="p-float-label">
                        <InputText id="in"  type="text" className="p-inputtext-lg" value={value} onChange={(e) => setValue(e.target.value)} placeholder="Enter AMP_ID" />
                    </span>
                </div>
                <div className="sub-section right-div">
                    <Button label="get the informations" className="p-button-secondary" />
                </div>
            </div>
        </div>
    );
};

export default Prediction;
