// /*
//  * decaffeinate suggestions:
//  * DS102: Remove unnecessary code created because of implicit returns
//  * DS207: Consider shorter variations of null checks
//  * Full docs: https://github.com/decaffeinate/decaffeinate/blob/master/docs/suggestions.md
//  */
// import React, { Component } from "react";
// import Popup2 from "./Popup2";
// import h from "react-hyperscript";
// import { Map, TileLayer, Popup, Marker, withLeaflet } from "react-leaflet";
// import {
//   FormGroup,
//   InputGroup,
//   Intent,
//   Switch,
//   Alignment,
// } from "@blueprintjs/core";
// import { DateInput, DatePicker, TimePrecision } from "@blueprintjs/datetime";
// import { Button } from "@blueprintjs/core";
// import { put } from "axios";
// import { StatefulComponent } from "@macrostrat/ui-components";
// import ReactJSON from "react-json-view";
// import update from "immutability-helper";
// //import {Map, TileLayer, Popup, Marker, withLeaflet} from "react-leaflet";
// import iconRetinaUrl from "leaflet/dist/images/marker-icon-2x.png";
// import iconUrl from "leaflet/dist/images/marker-icon.png";
// import shadowUrl from "leaflet/dist/images/marker-shadow.png";
// import L from "leaflet";
// import "leaflet/dist/leaflet.css";
// //import addMarkerClass from './mapping';

// var sub_status = 0;
// // function refreshPage() {
// //     window.location.reload(false);
// // };
// // Map icon sty;es
// delete L.Icon.Default.prototype._getIconUrl;
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl,
//   iconUrl,
//   shadowUrl,
// });

// // a list to host all markers
// var all_markers = [];

// const style = {
//   map: {
//     height: "400px",
//     width: "100%",
//   },
// };

// // Form component
// // vars for validation -- not 100% successful yet, need to work on this later
// var warning_fields = {};
// var checked = 0;

// function change_status(lat, lon, time, input) {
//   if (lat == null || lon == null || time == null) {
//     checked = 0;
//     return 0;
//   } else {
//     checked = 1;
//     return 1;
//   }
// }
// // return the real time validation
// function getIntent(input, min, max, name) {
//   if (input == null) {
//     return Intent.PRIMARY;
//   } else {
//     var data_in = parseFloat(input);
//     if (data_in >= min && data_in <= max) {
//       if (warning_fields[name] !== undefined) {
//         delete warning_fields[name];
//       }
//       return Intent.SUCCESS;
//     } else {
//       warning_fields[name] = 1;
//       return Intent.WARNING;
//     }
//   }
// }

// // function togglePopup() {
// //  this1.setState({
// //    showPopup: !this1.state.showPopup
// //  });
// //  //sub_status = 1
// // }

// // function sub(this1){
// //   //alert('Oh look, an alert!')
// //   return this1.submitData.bind(this1);
// // }

// class Form extends Component {
//   //initializing a component
//   constructor(props) {
//     // when run the class, also run it for the class that it is extending
//     super(props);
//     // this.state is @state
//     this.state = {
//       formData: { sample_text: null },
//       validate: 0,
//       sub_status: 0,
//       // for mapping the markers
//       markers: [],
//       showPopup: 0,
//       // for updating
//       markers1: { lat: null, lon: null },
//     };
//   }

//   // might be removed later
//   getMarkers = (e) => {
//     return e.markers;
//   };

//   // setting up function for markers
//   addMarker = (e) => {
//     var this_coor;
//     console.log("this coor 1: " + this_coor);
//     console.log("latlng: " + this.state.markers1);
//     const { markers } = this.state;
//     const lastMarker = markers[markers.length - 1];
//     markers.push(e.latlng);
//     all_markers.push([
//       markers.length,
//       e.latlng.lat.toFixed(5),
//       e.latlng.lng.toFixed(5),
//     ]);
//     // get the lat and lon of this coor
//     var new_coor = [
//       parseFloat(e.latlng.lat.toFixed(5)),
//       parseFloat(e.latlng.lng.toFixed(5)),
//     ];
//     const newState = update(this.state, {
//       //markers:{$set: e.latlng},
//       formData: {
//         ["lat"]: { $set: e.latlng.lat.toFixed(5) },
//         ["lon"]: { $set: e.latlng.lng.toFixed(5) },
//       },
//       markers1: {
//         ["lat"]: { $set: e.latlng.lat.toFixed(5) },
//         ["lon"]: { $set: e.latlng.lng.toFixed(5) },
//       },
//     });
//     this.setState(newState);
//     this_coor = [e.latlng.lat.toFixed(5), e.latlng.lng.toFixed(5)];
//     console.log("this coor:" + this_coor);
//     return this_coor;
//   };

//   render() {
//     // Map setup
//     var southWest = L.latLng(-85, -200),
//       northEast = L.latLng(85, 200),
//       mybounds = L.latLngBounds(southWest, northEast);
//     //update every key into the json view
//     // update the state in the form by the name of keys
//     const updater = (key) => {
//       return (event) => {
//         if (key == "lat" || key == "lon") {
//           const newState = update(this.state, {
//             formData: { [key]: { $set: event.target.value } },
//             // if it is lat and lon, also update markers1
//             markers1: { [key]: { $set: event.target.value } },
//           });
//           return this.setState(newState);
//         } else {
//           const newState = update(this.state, {
//             formData: { [key]: { $set: event.target.value } },
//           });
//           return this.setState(newState);
//         }
//         // update marker []
//         //all_markers = [this.state.markers]
//       };
//     };

//     // var updater2 = () => {
//     //   this.setState({
//     //    showPopup: 1
//     //    });
//     // };

//     // const sub2 = ()=>{
//     //   updater2();
//     //   sub(this);
//     // };

//     // const form_coordinate = () =>{ return event => {
//     //   if(this.state.markers1.lat != null || this.state.markers1.lon != null){
//     //     var new_coor = [parseFloat(this.state.markers1.lat), parseFloat(this.state.markers1.lon)];
//     //     const newState = update(this.state,{markers:{$set: new_coor}});
//     //     return this.setState(newState);
//     //   }
//     // }; };

//     // trying to update this.state.markers as a list containing coordinates
//     const form_coordinate = () => {
//       return (event) => {
//         if (
//           this.state.markers1.lat != null ||
//           this.state.markers1.lon != null
//         ) {
//           var new_coor = [
//             parseFloat(this.state.markers1.lat),
//             parseFloat(this.state.markers1.lon),
//           ];
//           all_markers.push([
//             this.state.markers.length,
//             parseFloat(this.state.markers1.lat),
//             parseFloat(this.state.markers1.lon),
//           ]);
//           data.push(new_coor);
//         }
//       };
//     };

//     // for validating, TBC
//     const toggleChecked = (lat, lon, time, checked) => {
//       return change_status(lat, lon, time, checked);
//     };

//     var data = all_markers;

//     //  const togglePopup=()=> {
//     //   sub_status = 1
//     //   this.setState({
//     //     showPopup: !this.state.showPopup
//     //   });
//     // }
//     //
//     const sub = () => {
//       if (this.state.showPopup == null) {
//         this.setState({
//           showPopup: 1,
//         });
//       }

//      alert('test')

//       this.submitData();
//     };

//     return h("div.form+map", [
//       <Map
//         center={[40, -100]}
//         onClick={this.addMarker}
//         zoom={5}
//         style={style.map}
//         //bounds = {mybounds}
//       >
//         <TileLayer
//           attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
//           url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}.png"
//           minZoom={3}
//           bounds={mybounds}
//         />
//         {this.state.markers.map((markers, idx) => (
//           <Marker key={`marker-${idx}`} position={markers}>
//             <Popup>
//               <span>
//                 {data[idx][1]}, {data[idx][2]}
//               </span>
//             </Popup>
//           </Marker>
//         ))}
//       </Map>,
//       h("div.shan-form", [
//         //h(ReactJSON, {src: this.state.markers}),
//         //h(ReactJSON, {src: data}),
//         //h(ReactJSON, {src: this.state.markers1}),
//         console.log("popup: " + this.state.showPopup),
//         console.log("this coor 2: " + this.state.markers),
//         console.log(this.state.formData),
//         console.log(Object.keys(this.state.formData).length),
//         console.log(warning_fields),

//         h("h2", "Sample location"),
//         h(
//           FormGroup,
//           {
//             helperText: "-90 to 90 degrees",
//             label: "Latitude",
//           },
//           [
//             h(InputGroup, {
//               id: "lat-text-inout",
//               placeholder: "Lat value",
//               value: this.state.formData.lat,
//               onChange: updater("lat"),
//               intent: getIntent(this.state.formData.lat, -90, 90, "lat"),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "-180 to 180 degrees",
//             label: "Longitude",
//           },
//           [
//             h(InputGroup, {
//               id: "lon-text-inout",
//               placeholder: "Lon value",
//               value: this.state.formData.lon,
//               onChange: updater("lon"),
//               intent: getIntent(this.state.formData.lon, -180, 180, "lon"),
//             }),
//           ]
//         ),
//         // h(Button, {
//         //   disabled: (this.state.formData.lat == null || this.state.formData.lon == null),
//         //   text: 'Map',
//         //   onClick: form_coordinate()
//         // }),
//         h(
//           FormGroup,
//           {
//             helperText: "General location. e.g. Northern Wisconsin",
//             label: "Location Name",
//           },
//           [
//             h(InputGroup, {
//               id: "location-text-inout",
//               placeholder: "Location",
//               value: this.state.formData.location,
//               onChange: updater("location"),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "in meters",
//             label: "Elevation",
//           },
//           [
//             h(InputGroup, {
//               id: "elevation-text-inout",
//               placeholder: "Elevation value",
//               value: this.state.formData.elevation,
//               onChange: updater("elevation"),
//             }),
//           ]
//         ),
//         h("h2", "Date of collecting"),
//         h(DatePicker, {
//           value: this.state.formData.calendarDate,
//           onChange: (result) => {
//             const newState = update(this.state, {
//               formData: { calendarDate: { $set: result } },
//             });
//             return this.setState(newState);
//           },
//         }),
//         h("h2", "General information of the sample"),

//         h(
//           FormGroup,
//           {
//             helperText: "Enter the import name. Leave it blank if NA",
//             label: "Import Name",
//           },
//           [
//             h(InputGroup, {
//               id: "import_name",
//               placeholder: "Import Name",
//               value: this.state.formData.import_name,
//               onChange: updater("import_name"),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "Enter the session index",
//             label: "Session",
//           },
//           [
//             h(InputGroup, {
//               id: "session-index-text-input",
//               placeholder: "Session index",
//               value: this.state.formData.session_index,
//               onChange: updater("session_index_text"),
//               intent: Intent.PRIMARY,
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "Enter the analysis name",
//             label: "Analysis name",
//           },
//           [
//             h(InputGroup, {
//               id: "analysis-name-text-input",
//               placeholder: "Analysis name text",
//               value: this.state.formData.analysis_name,
//               onChange: updater("analysis_text"),
//               intent: Intent.PRIMARY,
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "Enter the sample name",
//             label: "Sample",
//           },
//           [
//             h(InputGroup, {
//               id: "sample-text-input",
//               placeholder: "Sample text",
//               value: this.state.formData.sample_text,
//               onChange: updater("sample_text"),
//               intent: Intent.PRIMARY,
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "Enter the sample id",
//             label: "Sample ID",
//           },
//           [
//             h(InputGroup, {
//               id: "sample-id-input",
//               placeholder: "Sample ID",
//               value: this.state.formData.sample_id,
//               onChange: updater("sample_id"),
//               intent: Intent.PRIMARY,
//             }),
//           ]
//         ),
//         h("h2", "Sample analysis"),
//         h(
//           FormGroup,
//           {
//             helperText: "0-1",
//             label: "Shielding",
//           },
//           [
//             h(InputGroup, {
//               id: "shielding-text-inout",
//               placeholder: "Shielding value",
//               value: this.state.formData.shielding,
//               onChange: updater("shielding"),
//               intent: getIntent(
//                 this.state.formData.shielding,
//                 0,
//                 1,
//                 "shielding"
//               ),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "0-100",
//             label: "Quartz",
//           },
//           [
//             h(InputGroup, {
//               id: "quartz-text-inout",
//               placeholder: "Quartz value",
//               value: this.state.formData.quartz,
//               onChange: updater("quartz"),
//               intent: getIntent(this.state.formData.quartz, 0, 100, "quartz"),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "0-500",
//             label: "9Be Carrier",
//           },
//           [
//             h(InputGroup, {
//               id: "9be-text-inout",
//               placeholder: "9Be",
//               value: this.state.formData._9Be,
//               onChange: updater("_9Be"),
//               intent: getIntent(this.state.formData._9Be, 0, 500, "9Be"),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "1E-10 to 1E-20",
//             label: "10Be/9Be",
//           },
//           [
//             h(InputGroup, {
//               id: "be-ratio-text-inout",
//               placeholder: "10Be/9Be value",
//               value: this.state.formData.Be_ratio,
//               onChange: updater("Be_ratio"),
//               intent: getIntent(
//                 this.state.formData.Be_ratio,
//                 0.0000000000000000001,
//                 0.000000001,
//                 "10Be/9Be"
//               ),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "1E-10 to 1E-20",
//             label: "1 Sigma",
//           },
//           [
//             h(InputGroup, {
//               id: "1sig-text-inout",
//               placeholder: "1-sigma value",
//               value: this.state.formData._1_sigma,
//               onChange: updater("_1_sigma"),
//               intent: getIntent(
//                 this.state.formData._1_sigma,
//                 0.0000000000000000001,
//                 0.000000001,
//                 "1sigma"
//               ),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "0 to 1E-10, atoms/g",
//             label: "10Be",
//           },
//           [
//             h(InputGroup, {
//               id: "10be-text-inout",
//               placeholder: "10Be value",
//               value: this.state.formData._10Be,
//               onChange: updater("_10Be"),
//               intent: getIntent(
//                 this.state.formData._10Be,
//                 0,
//                 0.000000001,
//                 "10Be"
//               ),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "0 - 700 ka",
//             label: "10Be Age",
//           },
//           [
//             h(InputGroup, {
//               id: "10be-age-text-inout",
//               placeholder: "Age value",
//               value: this.state.formData.age,
//               onChange: updater("age"),
//               intent: getIntent(this.state.formData.age, 0, 700, "age"),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "0 to 1E-10, atoms/g",
//             label: "Uncertainty",
//           },
//           [
//             h(InputGroup, {
//               id: "uncertainty-text-inout",
//               placeholder: "Uncertainty value",
//               value: this.state.formData.uncertainty,
//               onChange: updater("uncertainty"),
//               intent: getIntent(
//                 this.state.formData.uncertainty,
//                 0,
//                 0.000000001,
//                 "uncertainty"
//               ),
//             }),
//           ]
//         ),
//         h(
//           FormGroup,
//           {
//             helperText: "Enter additional information",
//             label: "Notes",
//           },
//           [
//             h(InputGroup, {
//               id: "notes-text-inout",
//               placeholder: "Notes or comments",
//               value: this.state.formData.notes,
//               onChange: updater("notes"),
//             }),
//           ]
//         ),
//         h("h2", "Validating"),
//         h("h3", "Data preview"),
//         h(ReactJSON, { src: this.state.formData }),
//         h(
//           "p",
//           "Empty field(s): " +
//             (19 - Object.keys(this.state.formData).length).toString()
//         ),
//         h(
//           "p",
//           "Invalid field(s): " + Object.keys(warning_fields).length.toString()
//         ),
//         h("p", "Submission: " + sub_status.toString()),
//         h("p", "popup: " + this.state.showPopup.toString()),
//         h(Switch, {
//           disabled:
//             this.state.formData.lat == null ||
//             this.state.formData.lon == null ||
//             this.state.formData.calendarDate == null,
//           label: "Have all required fields: lat, lon and date.",
//           defaultChecked: false,
//           checked: toggleChecked(
//             this.state.formData.lat,
//             this.state.formData.lon,
//             this.state.formData.calendarDate,
//             checked
//           ),
//           //onChange: toggleChecked(this.state.formData.lat, this.state.formData.lon, this.state.formData.calendarDate,checked),
//           innerLabelChecked: "Yes",
//           innerLabel: "No",
//           alignIndicator: Alignment.RIGHT,
//           inline: true,
//         }),
//         console.log(checked.toString() + " check"),
//         h("p", ""),
//         h(Button, {
//           disabled: checked == 0,
//           text: "Submit",
//           onClick: () => sub(),
//         }),
//         // h(Popup2, {
//         // }),
//         // h(Button, {
//         //   text: 'Clear',
//         //   onClick: window.location.reload(false)
//         // }),
//         console.log("sub_status: " + this.state.sub_status),
//       ]),
//     ]);
//   }

//   async submitData() {
//     //@ ref to right value "=>" instead of "->"
//     var lat_data,
//       lon_data,
//       uncertainty_data,
//       session_index_data,
//       age_data,
//       shielding_data,
//       elevation_data,
//       sigma_data,
//       quartz_data,
//       _9Be_data,
//       _10Be_data,
//       ratio_Be_data;

//     lat_data = parseFloat(this.state.formData.lat);
//     lon_data = parseFloat(this.state.formData.lon);

//     if (this.state.formData.elevation == null) {
//       elevation_data = 0;
//     } else {
//       elevation_data = parseFloat(this.state.formData.elevation);
//     }

//     if (this.state.formData.session_index == null) {
//       session_index_data = 0;
//     } else {
//       session_index_data = parseFloat(this.state.formData.session_index);
//     }

//     if (this.state.formData.age == null) {
//       age_data = 0;
//     } else {
//       age_data = parseFloat(this.state.formData.age);
//     }

//     if (this.state.formData.uncertainty == null) {
//       uncertainty_data = 0;
//     } else {
//       uncertainty_data = parseFloat(this.state.formData.uncertainty);
//     }

//     if (this.state.formData._1_sigma == null) {
//       sigma_data = 0;
//     } else {
//       sigma_data = parseFloat(this.state.formData._1_sigma);
//     }

//     if (this.state.formData.shielding == null) {
//       shielding_data = 0;
//     } else {
//       shielding_data = parseFloat(this.state.formData.shielding);
//     }

//     if (this.state.formData.quartz == null) {
//       quartz_data = 0;
//     } else {
//       quartz_data = parseFloat(this.state.formData.quartz);
//     }

//     if (this.state.formData._9Be == null) {
//       _9Be_data = 0;
//     } else {
//       _9Be_data = parseFloat(this.state.formData._9Be);
//     }

//     if (this.state.formData._10Be == null) {
//       _10Be_data = 0;
//     } else {
//       _10Be_data = parseFloat(this.state.formData._10Be);
//     }

//     if (this.state.formData.Be_ratio == null) {
//       ratio_Be_data = 0;
//     } else {
//       ratio_Be_data = parseFloat(this.state.formData.Be_ratio);
//     }

//     console.log("placeholder");

//     const sessionData = {
//       date: this.state.formData.calendarDate,
//       name: this.state.formData.import_name,
//       sample: {
//         name: this.state.formData.sample_text,
//         elevation: elevation_data,
//         location_name: this.state.formData.location,
//         location: {
//           type: "Point",
//           coordinates: [lon_data, lat_data],
//         },
//       },
//       analysis: [
//         {
//           // Can't seem to get or create this instance from the database
//           analysis_type: this.state.formData.analysis_name,
//           session_index: this.state.formData.session_index,
//           datum: [
//             {
//               value: _9Be_data,
//               error: null,
//               type: {
//                 parameter: "9Be carrier",
//                 unit: "",
//               },
//             },
//             {
//               value: _10Be_data,
//               error: null,
//               type: {
//                 parameter: "10Be",
//                 unit: "atoms/g",
//               },
//             },
//             {
//               value: ratio_Be_data,
//               error: null,
//               type: {
//                 parameter: "10Be/9Be",
//                 unit: "none",
//               },
//             },
//             {
//               value: age_data,
//               error: uncertainty_data,
//               type: {
//                 parameter: "10Be Age",
//                 unit: "ka",
//               },
//             },
//             {
//               value: shielding_data,
//               error: null,
//               type: {
//                 parameter: "Sheilding",
//                 unit: "none",
//               },
//             },
//             {
//               value: quartz_data,
//               error: null,
//               type: {
//                 parameter: "Quartz",
//                 unit: "none",
//               },
//             },
//             {
//               value: sigma_data,
//               error: null,
//               type: {
//                 parameter: "1 Sigma",
//                 unit: "none",
//               },
//             },
//             {
//               value: 1,
//               error: null,
//               type: {
//                 parameter: "Data source",
//                 unit: "none",
//               },
//             },
//           ],
//         },
//       ],
//     };

//     const data = {
//       filename: null,
//       data: sessionData,
//     };
//     //console.log(data);
//     // const updater = key => { return event => {
//     //     const newState = update(this.state, {[key]:{$set: 1}});
//     //     return this.setState(newState);
//     // }};
//     console.log(JSON.stringify(data));
//     // try {
//     //   const res = await put("/api/v1/import-data/session", data);
//     //   //() => window.location.reload(false);

//     //   //this.togglePopup.bind(this)
//     //   return console.log(res);
//     // } catch (error) {
//     //   console.error(error);
//       // expected output: ReferenceError: nonExistentFunction is not defined
//       // Note - error messages will vary depending on browser
//     }
//   }
// }

// export default Form;
