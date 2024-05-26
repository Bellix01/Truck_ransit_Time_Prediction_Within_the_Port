import React, { useEffect, useState } from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { InputText } from 'primereact/inputtext';
import { Button } from 'primereact/button';
import copy from 'clipboard-copy';
import './Prediction.css'; 
import './Home.css' 

const Prediction = () => {
    const [trucks, setTrucks] = useState([]);
    const [truckInfo, setTruckInfo] = useState([]);
    const [globalFilter, setGlobalFilter] = useState("");
    const [copyRowId, setCopyRowId] = useState(null);
    const [showCopiedMessage, setShowCopiedMessage] = useState(false);
    const [value, setValue] = useState("");
    const [showInfoCard, setShowInfoCard] = useState(false);
    const [predictionvalue, setPredictionValue] = useState("");
    const [predictionVisible, setPredictionVisible] = useState(false);
    const [predictions, setPredictions] = useState([]);
    const [fetchingIntervalId, setFetchingIntervalId] = useState(null);

    // Load predictions from localStorage on component mount
    
    // const savedPredictions = localStorage.getItem('predictions');
    // useEffect(() => {
       
    //     if (savedPredictions) {
    //         setPredictions(JSON.parse(savedPredictions));
    //     }
    // }, []);

    // // Save predictions to localStorage whenever they change
    // useEffect(() => {
    //     localStorage.setItem('predictions', JSON.stringify(predictions));
    // }, [predictions]);

    useEffect(() => {
        fetchTruckData();
        fetchPredictions();
     
    }, []);

    // Fetch truck data from Flask backend
    const fetchTruckData = () => {
        fetch("http://127.0.0.1:5000/")
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setTrucks(data);
            })
            .catch(error => console.error("Error fetching truck data:", error));
    };

    // Fetch predictions from Flask backend
    const fetchPredictions = () => {
        fetch("http://127.0.0.1:5000/display_predictions")
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                setPredictions(data);
            
               
                
            })
            .catch(error => console.error("Error fetching predictions:", error));
    };

    // Fetching a specific row from data
    const getDataRow = () => {
        fetch("http://127.0.0.1:5000/get_truck_info", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ AMP_ID: value })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            setTruckInfo(data);
            setShowInfoCard(true);
            setPredictionVisible(false);
        })
        .catch(error => console.error("Error fetching truck info:", error));
    };

    // Check if AMP ID exists in the database
    const checkAmpIdExists = (ampId) => {
        return fetch(`http://127.0.0.1:5000/check_amp_id_exists`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ amp_id: ampId })
        })
        .then(response => response.json())
        .then(data => data.exists)
        .catch(error => {
            console.error("Error checking AMP ID:", error);
            return false;
        });
    };

    const getPrediction = () => {
        fetch("http://127.0.0.1:5000/get_prediction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(truckInfo)
        })
        .then(response => response.json())
        .then(data => {
            setPredictionValue(data);
            setPredictionVisible(true);
            setTimeout(() => {
                setPredictionVisible(false);
            }, 5000);
            const fetchedData = {
                ampId: value, 
                predictionValue: data // Use the updated prediction value
            };

            checkAmpIdExists(fetchedData.ampId).then(ampIdExists => {
                if (!ampIdExists) {
                    // If AMP ID does not exist, store the new prediction
                    fetch("http://127.0.0.1:5000/predictions", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ amp_id: value, prediction_value: data })
                    })
                    .then(response => response.json())
                    .then(() => {
                        // Update predictions state
                        setPredictions([...predictions, fetchedData]);

                        fetchPredictions();
                    })
                    .catch(error => console.error("Error storing prediction:", error));
                }
            });
        })
        .catch(error => console.error("Error fetching prediction:", error));
    };
    

    // Part of copy button
    const handleCopy = (ampId) => {
        copy(ampId);
        setShowCopiedMessage(true);
 
        setTimeout(() => {
            setShowCopiedMessage(false);
        }, 500);
    };

    const handleRowEnter = (rowData) => {
        setCopyRowId(rowData.AMP_ID);
    };
    
    const handleRowLeave = () => {
        setCopyRowId(null);
    };
    
    const renderCopyButton = (rowData) => {
        const isCopyVisible = rowData.AMP_ID === copyRowId;
    
        return (
            <div
                onMouseEnter={() => handleRowEnter(rowData)}
                onMouseLeave={handleRowLeave}
                className="copy-button-container"
            >
                <span>{rowData.AMP_ID}</span>
                {isCopyVisible && (
                    <>
                    <Button 
                        icon="pi pi-copy"
                        className="copy-icon" 
                        tooltip=""
                        onClick={() => handleCopy(rowData.AMP_ID)} 
                    />
                    {showCopiedMessage && <span className="copied-message">Copied</span>}
                </>
                )}
            </div>
        );
    };

    // Part of search and clear
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
    
    const footer = <p className="table-footer">Total records = {trucks ? trucks.length : 0}</p>;

    return (
        <div className="container">
            <div className="top-container">
                <div className="table-wrapper">
                    <DataTable
                        value={trucks}
                        paginator
                        removableSort
                        rows={5}
                        scrollable
                        scrolldirection="horizontal"
                        tableStyle={{ minWidth: '50rem' }}
                        className="custom-table"
                        header={header}
                        globalFilter={globalFilter}
                        footer={footer}
                    >
                        <Column field="AMP_ID" header="AMP ID" sortable style={{ width: '10%' }} body={renderCopyButton} ></Column>  
                        <Column field="TYPE_UNITE" header="Type Unite" sortable style={{ width: '15%' }}></Column>
                        <Column field="SS_TYPE_UNITE" header="SS Type Unite" sortable style={{ width: '15%' }}></Column>
                        <Column field="VIDE_PLEIN" header="Vide/Plein" sortable style={{ width: '10%' }}></Column>
                        <Column field="NATURE_MARCHANDISE" header="Nature Marchandise" sortable style={{ width: '15%' }}></Column>
                        <Column field="TERMINAL" header="Terminal" sortable style={{ width: '10%' }}></Column>
                        <Column field="POIDS" header="Poids" sortable style={{ width: '10%' }}></Column>
                        <Column field="COULOIR" header="Couloir" sortable style={{ width: '10%' }}></Column>
                        <Column field="DATE_ZRE" header="Date ZRE" sortable style={{ width: '15%' }}></Column>
                    </DataTable>
                </div>
                <div className="card-section">
                    <h2 className="card-section-title">Historic</h2>
                    <div className="card-scroll">
                        {predictions.length > 0 ? (
                            predictions.map((prediction, index) => (
                                <div key={index} className="card-content">
                                    <h3>AMP ID: {prediction.amp_id}</h3>
                                    <p>Prediction Value: {prediction.prediction_value}</p>
                                </div>
                            ))
                        ) : (
                            <p>No predictions yet.</p>
                        )}
                    </div>
                </div>
            </div>
            <div className="predict-section">
                <div className="sub-section left-div">
                    <h2 className="">Truck Transit Time</h2>
                    <h5>Enter the AMP_ID to get the specific truck information.</h5>
                    <span className="p-float-label">
                        <InputText id="in" type="text" className="p-inputtext-lg" value={value} onChange={(e) => setValue(e.target.value)} placeholder="Enter AMP_ID" />
                    </span>
                </div>
                <div className="sub-section right-div">
                    <Button label="Get Information" className="p-button-secondary" onClick={getDataRow}/>
                </div>
            </div>
            {showInfoCard && (
                <div className="get-info-section">
                    <div className="truck-info-card">
                        {truckInfo ? (
                            <>
                                <p><span>Type Unite:</span> {truckInfo.TYPE_UNITE}</p>
                                <p><span>SS Type Unite:</span> {truckInfo.SS_TYPE_UNITE}</p>
                                <p><span>Vide Plein:</span> {truckInfo.VIDE_PLEIN}</p>
                                <p><span>Nature Marchandise:</span> {truckInfo.NATURE_MARCHANDISE}</p>
                                <p><span>Terminal:</span> {truckInfo.TERMINAL}</p>
                                <p><span>Poids:</span> {truckInfo.POIDS}</p>
                                <p><span>Couloir:</span> {truckInfo.COULOIR}</p>
                                <p><span>Date ZRE:</span> {truckInfo.DATE_ZRE}</p>
                                <Button label="Get Prediction" className="p-button-secondary prediction-button" onClick={getPrediction} />
                            </>
                        ) : (
                            <p>No information available</p>
                        )}
                    </div>
                </div>
            )}
            <div className={`predict-value-card ${predictionVisible ? '' : 'hidden'}`}>
                <p><span className="predict-value">Transit Time:</span> {predictionvalue} h</p>
            </div>
        </div>
    );
};

export default Prediction;
