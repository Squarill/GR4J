import gradio as gr
import queue
import threading
import uuid
import callbacks as cb

"""
A NOTE FOR MYSELF
@gr.render
"""

"""****************** SIMULATE TAB ******************"""

def build_simulate_tab(simulate_btn_fn: callable = None, file_uploaded_fn: callable = None):
    with gr.Tab(label="Simulate") as simulate_tab:
        if simulate_btn_fn is None:
            gr.Warning("Simulation button function is not defined.")
            gr.Markdown("### This tab cannot be loaded since the simulation button function is not defined.")
            return simulate_tab
        with gr.Row(equal_height=True):
            dataset = gr.File(file_count="single", file_types=[".npz"], label="Dataset")
            area = gr.Number(label="Catchment Area (km²) (will override the existing embedded area value in the dataset)")
            warmup_days = gr.Number(label="Warmup Days", value=1460)
        with gr.Row(equal_height=True):
            with gr.Column():
                X1 = gr.Slider(label="X1", interactive=True, minimum=0, maximum=2000, step=1)
                X2 = gr.Slider(label="X2", interactive=True, minimum=-10, maximum=10, step=0.1)
                X3 = gr.Slider(label="X3", interactive=True, minimum=0, maximum=300, step=1)
                X4 = gr.Slider(label="X4", interactive=True, minimum=1.1, maximum=15.0, step=0.1)
                S = gr.Slider(label="S", interactive=True, minimum=0, maximum=2000, step=1)
                R = gr.Slider(label="R", interactive=True, minimum=0, maximum=300, step=1)
                simulate_btn = gr.Button("Simulate")
                with gr.Row(equal_height=True):
                    simulate_nse = gr.Textbox(label="NSE", scale=1, interactive=False)
                    plot_start_year = gr.DateTime(value="YYYY-MM-DD", label="Graph Start Date", include_time=False)
                    plot_end_year = gr.DateTime(value="YYYY-MM-DD", label="Graph End Date", include_time=False)
            graph = gr.Plot(label="Hydrograph and Hyteograph")

        #Callbacks
        simulate_btn.click(fn = simulate_btn_fn, inputs=[X1, X2, X3, X4, S, R, dataset, area, warmup_days, plot_start_year, plot_end_year], outputs=[simulate_nse, graph])
        dataset.change(fn = file_uploaded_fn, inputs=[dataset], outputs=[plot_start_year, plot_end_year, area])
        
        return simulate_tab


"""****************** DATA PREPARATION TAB ******************"""

def build_GR4J_data_preparation_tab(session_id: str = None, prepare_btn_fn: callable = None, file_uploaded_fn: callable = None):
    with gr.Tab(label="GR4J Data Preparation") as GR4J_data_preparation_tab:
        with gr.Row(equal_height=True):
            with gr.Column():
                P_data = gr.File(file_count="single", file_types=[".npz", ".txt"], label="Precipitation Data (mm/day)")
                with gr.Row(equal_height=True):
                    P_data_start = gr.DateTime(label="Data Start Date", include_time=False, interactive=False)
                    P_data_end = gr.DateTime(label="Data End Date", include_time=False, interactive=False)
            
            with gr.Column():
                PET_data = gr.File(file_count="single", file_types=[".npz", ".txt"], label="PET Data (mm/day)")
                with gr.Row(equal_height=True):
                    PET_data_start = gr.DateTime(label="Data Start Date", include_time=False, interactive=False)
                    PET_data_end = gr.DateTime(label="Data Start Date", include_time=False, interactive=False)
            
            with gr.Column():
                Q_obs_data = gr.File(file_count="single", file_types=[".npz", ".txt"], label="Q Data (m³/s)")
                with gr.Row(equal_height=True):
                    Q_obs_data_start = gr.DateTime(label="Data Start Date", include_time=False, interactive=False)
                    Q_obs_data_end = gr.DateTime(label="Data Start Date", include_time=False, interactive=False)
            
            area = gr.Number(label="Catchment Area (km²)")

        with gr.Row(equal_height=True):
            with gr.Column():
                start_date = gr.DateTime(label="Start Date", include_time=False, type="string")
                end_date = gr.DateTime(label="End Date", include_time=False, type="string")
        
        with gr.Row(equal_height=True):
            output_name = gr.Textbox(label="Output File Name")
            prepare_btn = gr.Button("Prepare Data")
            output_data = gr.File(file_count="single", file_types=[".npz"], label="Output Data", interactive=False)
            
        #Callbacks
        P_data.change(fn = file_uploaded_fn, inputs=[P_data], outputs=[P_data_start, P_data_end])
        PET_data.change(fn = file_uploaded_fn, inputs=[PET_data], outputs=[PET_data_start, PET_data_end])
        Q_obs_data.change(fn = file_uploaded_fn, inputs=[Q_obs_data], outputs=[Q_obs_data_start, Q_obs_data_end])
        prepare_btn.click(fn = prepare_btn_fn, inputs=[P_data, PET_data, Q_obs_data, area, start_date, end_date, output_name, session_id], outputs=[output_data])

        return GR4J_data_preparation_tab

def build_data_kit():
    with gr.Row(equal_height=True, visible=True, height=85) as kit:
        dataset_path = gr.File(file_count="single", file_types=[".npz", ".txt"], label="Dataset", height=85, scale = 2)
        data_start_date = gr.DateTime(label="Data Start Date", include_time=False, interactive=False, scale = 1)
        data_end_date = gr.DateTime(label="Data End Date", include_time=False, interactive=False, scale = 1)
        data_to_be_extracted = gr.Dropdown(choices=[], label="Data to be Extracted", interactive=True, scale = 1)
        extracted_data_tag = gr.Textbox(label="Extracted Data Tag Name", interactive=True, type="text", scale = 1)
        
        #Callbacks
        dataset_path.change(fn = cb.data_kit_file_uploaded, inputs=[dataset_path], outputs=[data_to_be_extracted, extracted_data_tag, data_start_date, data_end_date])

        return kit, [dataset_path, data_to_be_extracted, extracted_data_tag]

def build_core_data_preparation_tab(session_id: str = None):
    with gr.Tab(label="Core Data Preparation") as core_data_preparation_tab:
        with gr.Row():
            with gr.Column(scale=2):
                dataset_dict = {}
                s1, dataset_dict["s1"] = build_data_kit()
                s2, dataset_dict["s2"] = build_data_kit()
                s3, dataset_dict["s3"] = build_data_kit()
                s4, dataset_dict["s4"] = build_data_kit()
                s5, dataset_dict["s5"] = build_data_kit()
                s6, dataset_dict["s6"] = build_data_kit()
                s7, dataset_dict["s7"] = build_data_kit()
                s8, dataset_dict["s8"] = build_data_kit()
                s9, dataset_dict["s9"] = build_data_kit()
                s10, dataset_dict["s10"] = build_data_kit()
                dataset_list = []
                for _,value in dataset_dict.items():
                    for v in value:
                        dataset_list.append(v)
                

            with gr.Column(scale=1):
                area = gr.Number(label="Catchment Area (km²)")
                start_date = gr.DateTime(label="Start Date", include_time=False, type="string")
                end_date = gr.DateTime(label="End Date", include_time=False, type="string")
                output_name = gr.Textbox(label="Output File Name")
                prepare_btn = gr.Button("Prepare Data")
                output_file = gr.File(label="Output File", interactive=False)

        #Callbacks
        prepare_btn.click(fn = cb.DataPrep_core_data_preparation_btn, inputs=[start_date, end_date, area, output_name, session_id, *dataset_list], outputs=[output_file])
        return core_data_preparation_tab

def build_GEE_exporter_tab(session_id, exporter_service = None, export_btn_fn: callable = None):
    with gr.Tab(label="GEE Exporter") as GEE_exporter_tab:
        if exporter_service is None:
            gr.Warning("Exporter is not defined.")
            gr.Markdown("### This tab cannot be loaded since the exporter is not defined.")
            return GEE_exporter_tab
        
        exporter_service = gr.State(value=exporter_service)

        geojson = gr.File(file_count="single", file_types=[".geojson"], label="GeoJSON File (geometry data)")
        choices = [
            "temperature_2m",
            "temperature_2m_min",
            "temperature_2m_max", 
            "surface_net_solar_radiation_sum",
            "surface_net_thermal_radiation_sum",
            "u_component_of_wind_10m",
            "v_component_of_wind_10m",
            "surface_pressure",
            "dewpoint_temperature_2m",
            "total_precipitation_sum"
        ]
        variables = gr.CheckboxGroup(
            choices=choices,
            label = "Variables to be exported"
        )

        start_date = gr.DateTime(label = "Start Date", include_time=False, interactive=True, type = "string")
        end_date = gr.DateTime(label = "End Date", include_time=False, interactive=True, type = "string")

        output_name = gr.Textbox(value = "GEE_EXPORT_DATA.npz", label="Output File Name", interactive=True)

        export_btn = gr.Button("Export")
        with gr.Row(equal_height=True):
            exported_dataset = gr.File(file_count="single", file_types=[".npz"], label="Exported Data", interactive=False)
            log = gr.Textbox(label="Log", interactive=False)

        #Callbacks
        export_btn.click(fn = export_btn_fn, inputs=[session_id, output_name, geojson, variables, start_date, end_date, exporter_service], outputs=[exported_dataset, log])


        return GEE_exporter_tab

def build_penman_monteith_tab(session_id, penman_monteith_btn_fn: callable = None):
    with gr.Tab(label="Penman-Monteith") as penman_monteith_tab:
        with gr.Row(equal_height=True):
            with gr.Column():
                gr.Markdown("# Input Variables Required In The Dataset:")
                inputs = "temperature_2m\ntemperature_2m_min\ntemperature_2m_max\nsurface_net_solar_radiation_sum\nsurface_net_thermal_radiation_sum\nu_component_of_wind_10m\nv_component_of_wind_10m\nsurface_pressure\ndewpoint_temperature_2m"
                gr.Markdown(inputs)
            with gr.Column():
                gr.Markdown("# Output:")
                gr.Markdown("Potential Evapotranspiration (mm/day)")
        
        output_name = gr.Textbox(value = "PET_DATA.npz", label="Output File Name", interactive=True)

        with gr.Row(equal_height=True):
            dataset = gr.File(file_count="single", file_types=[".npz"], label="Dataset from GEE Exporter")
            PET_output = gr.File(file_count="single", file_types=[".npz"], label="PET Output", interactive=False)

        #Callbacks
        dataset.change(fn=penman_monteith_btn_fn, inputs=[session_id, dataset, output_name], outputs=PET_output)

def build_dataset_calculator(file_uploaded_fn: callable = None, calculate_btn_fn: callable = None):
    with gr.Tab(label="Dataset Calculator") as dataset_calculator:
        with gr.Row(equal_height=True):
            input_dataset = gr.File(file_count="single", file_types=[".npz"], label="Dataset")
            variable = gr.Dropdown(choices = ["All"], label="Variable", interactive=True)
            operators = ["Add", "Subtract", "Multiply", "Divide", "Change Variable Name"]
            operator = gr.Dropdown(choices=operators, label="Operator", interactive=True)
            number = gr.Textbox(label="Number", interactive=True, type="text")
            output_dataset = gr.File(file_count="single", file_types=[".npz"], label="Output Dataset", interactive=False)

        calculate_btn = gr.Button("Calculate")

        #Callbacks
        input_dataset.change(fn=file_uploaded_fn, inputs=[input_dataset], outputs=[variable])
        calculate_btn.click(fn=calculate_btn_fn, inputs=[input_dataset, operator, number, variable], outputs=output_dataset)

def build_dataset_observer():
    with gr.Tab(label="Dataset Observer") as dataset_observer:
        with gr.Row(equal_height=True):
            dataset = gr.File(file_count="single", file_types=[".npz"], label="Dataset")
            with gr.Column():
                dataset_start_date = gr.DateTime(label="Data Start Date", include_time=False, interactive=False, type="string")
                dataset_end_date = gr.DateTime(label="Data End Date", include_time=False, interactive=False, type="string")
        
        data = gr.Dropdown(choices=[], label="Data to be Observed", interactive=True, type="value")

        with gr.Row(equal_height=True):
            with gr.Column():
                with gr.Row(equal_height=True):
                    plot = gr.Plot(label="Plot of the Selected Data", scale=2)
                    data_info = gr.DataFrame(label="Data", interactive=False, type="pandas", scale=1)
                    with gr.Column(scale=1):
                        observe_start_date = gr.DateTime(label="Observe Start Date", include_time=False, interactive=True, type="string")
                        observe_end_date = gr.DateTime(label="Observe End Date", include_time=False, interactive=True, type="string")
                        observe_btn = gr.Button("Observe")

        #Callbacks
        dataset.change(fn=cb.DataPrep_dataset_observer_file_uploaded, inputs=[dataset], outputs=[dataset_start_date, dataset_end_date, observe_start_date, observe_end_date, data])
        data.change(fn = cb.DataPrep_observe_btn, inputs=[dataset, data, observe_start_date, observe_end_date], outputs=[plot, data_info])
        observe_btn.click(fn = cb.DataPrep_observe_btn, inputs=[dataset, data, observe_start_date, observe_end_date], outputs=[plot, data_info])

        return dataset_observer

def build_data_preparation_tab(session_id: str = None, prepare_btn_fn: callable = None, GR4J_file_uploaded_fn: callable = None, export_btn_fn: callable = None, exporter_service = None, penman_monteith_btn_fn: callable = None, calculator_file_uploaded_fn: callable = None, calculater_btn_fn: callable = None):
    with gr.Tab(label="Data Preparation") as data_preparation_tab:
        session_id = gr.State(value=session_id)
        build_GR4J_data_preparation_tab(session_id=session_id, prepare_btn_fn=prepare_btn_fn, file_uploaded_fn=GR4J_file_uploaded_fn)
        build_GEE_exporter_tab(session_id=session_id, export_btn_fn=export_btn_fn, exporter_service=exporter_service)
        build_penman_monteith_tab(session_id=session_id, penman_monteith_btn_fn=penman_monteith_btn_fn)
        build_dataset_calculator(file_uploaded_fn=calculator_file_uploaded_fn, calculate_btn_fn=calculater_btn_fn)
        build_core_data_preparation_tab(session_id=session_id)
        build_dataset_observer()
        return data_preparation_tab

"""****************** CALIBRATE AND VALIDATE TAB ******************"""

def build_GR4J_calibrate_and_validate_tab(calibrate_btn_fn: callable = None, validate_btn_fn: callable = None, file_uploaded_fn: callable = None):
    with gr.Tab(label="GR4J Calibrate and Validate") as GR4J_calibrate_and_validate_tab:
        gr.Markdown("# P (mm/day), PET (mm/day), Q (m³/s)")
        module = gr.Dropdown(choices=[
            "GR4J",
            "GR4J + CemaNeige"
        ], label="Module", interactive=True, type="value")
        with gr.Row(equal_height=True):
            with gr.Column():
                calibration_dataset = gr.File(file_count="single", file_types=[".npz"], label="Calibration Data")
                calibration_area = gr.Number(label="Embedded Area", interactive=False)
                calibration_data_start_date = gr.DateTime(label = "Data Start Date", include_time=False, interactive=False)
                calibration_data_end_date = gr.DateTime(label = "Data End Date", include_time=False, interactive=False)

            with gr.Column():
                validation_dataset = gr.File(file_count="single", file_types=[".npz"], label="Validation Data")
                validation_area = gr.Number(label="Embedded Area", interactive=False)
                validation_data_start_date = gr.DateTime(label = "Data Start Date", include_time=False, interactive=False)
                validation_data_end_date = gr.DateTime(label = "Data End Date", include_time=False, interactive=False)

            with gr.Column():
                area = gr.Number(label="Catchment Area (km²) (will override the embedded area value in the dataset)")
                calibration_warmup_days = gr.Number(label="Calibration Warmup Days", value=1460, interactive=True)
                validation_warmup_days = gr.Number(label="Validation Warmup Days", value=0, interactive=True)

        with gr.Row(equal_height=True):
            maxiter = gr.Number(label="Max Iterations", value=100, interactive=True)
            popsize = gr.Number(label="Population Size", value=20, interactive=True)
            cpu_count = gr.Number(label="CPU Count (-1 for all of them)", value=-1, interactive=True)
            tolerance = gr.Number(label="Tolerance", value=1e-7, interactive=True)
            object_function = gr.Dropdown(("NSE", "KGE"), label="Object Function", value="NSE", interactive=True)
            calibrate_btn = gr.Button("Calibrate")
        
        with gr.Row(equal_height=True):
            with gr.Row(equal_height=True, scale = 5):
                X1 = gr.Number(label="X1", interactive=False)
                X2 = gr.Number(label="X2", interactive=False)
                X3 = gr.Number(label="X3", interactive=False)
                X4 = gr.Number(label="X4", interactive=False)
                X5 = gr.Number(label="X5", interactive=False, visible=False)
                X6 = gr.Number(label="X6", interactive=False, visible=False)
                S = gr.Number(label="S", interactive=True)
                R = gr.Number(label="R", interactive=True)
                G = gr.Number(label="G", interactive=True, visible=False)
                eTG = gr.Number(label="eTG", interactive=True, visible=False)
            with gr.Column(scale = 1):
                validate_btn = gr.Button("Validate")
            warning_text = gr.Markdown("## Warning!\nIf the validation set does not start right after the calibration set, set S and R values as 0 and add a validation warmup day value above.", scale = 1)
        with gr.Row(equal_height=True):
            with gr.Column(scale = 1):
                validation_output_NSE = gr.Textbox(label="NSE on Validation Set",interactive=False)
                validation_output_KGE = gr.Textbox(label="KGE on Validation Set",interactive=False)
            graph = gr.Plot(label="Hydrograph and Hyteograph")
    
        #Callbacks
        calibrate_btn.click(fn = cb.CaV_calibrate_btn, inputs=[calibration_dataset, area, calibration_warmup_days, maxiter, popsize, cpu_count, tolerance, object_function, module], outputs=[X1, X2, X3, X4, X5, X6, S, R, G, eTG])
        validate_btn.click(fn = cb.CaV_validate_btn, inputs=[X1, X2, X3, X4, X5, X6, S, R, G, eTG, validation_dataset, area, validation_warmup_days, module], outputs=[validation_output_NSE, validation_output_KGE, graph])

        calibration_dataset.change(fn = file_uploaded_fn, inputs=[calibration_dataset], outputs=[calibration_area, calibration_data_start_date, calibration_data_end_date])
        validation_dataset.change(fn = file_uploaded_fn, inputs=[validation_dataset], outputs=[validation_area, validation_data_start_date, validation_data_end_date])

        module.change(fn=cb.CaV_module_change,inputs=module, outputs=[X5, X6, G, eTG])
        return GR4J_calibrate_and_validate_tab

def build_GR4J_CN_calibrate_and_validate_tab(calibrate_btn_fn: callable = None, validate_btn_fn: callable = None, file_uploaded_fn: callable = None):
    with gr.Tab(label="GR4J Calibrate and Validate") as GR4J_calibrate_and_validate_tab:
        gr.Markdown("# P (mm/day), PET (mm/day), T_avg (°C), Q (m³/s)")
        with gr.Row(equal_height=True):
            with gr.Column():
                calibration_dataset = gr.File(file_count="single", file_types=[".npz"], label="Calibration Data")
                calibration_area = gr.Number(label="Embedded Area", interactive=False)
                calibration_data_start_date = gr.DateTime(label = "Data Start Date", include_time=False, interactive=False)
                calibration_data_end_date = gr.DateTime(label = "Data End Date", include_time=False, interactive=False)

            with gr.Column():
                validation_dataset = gr.File(file_count="single", file_types=[".npz"], label="Validation Data")
                validation_area = gr.Number(label="Embedded Area", interactive=False)
                validation_data_start_date = gr.DateTime(label = "Data Start Date", include_time=False, interactive=False)
                validation_data_end_date = gr.DateTime(label = "Data End Date", include_time=False, interactive=False)

            with gr.Column():
                area = gr.Number(label="Catchment Area (km²) (will override the embedded area value in the dataset)")
                calibration_warmup_days = gr.Number(label="Calibration Warmup Days", value=1460, interactive=True)
                validation_warmup_days = gr.Number(label="Validation Warmup Days", value=0, interactive=True)

        with gr.Row(equal_height=True):
            maxiter = gr.Number(label="Max Iterations", value=100, interactive=True)
            popsize = gr.Number(label="Population Size", value=20, interactive=True)
            cpu_count = gr.Number(label="CPU Count (-1 for all of them)", value=-1, interactive=True)
            tolerance = gr.Number(label="Tolerance", value=1e-7, interactive=True)
            object_function = gr.Dropdown(("NSE", "KGE"), label="Object Function", value="NSE", interactive=True)
            calibrate_btn = gr.Button("Calibrate")
        
        with gr.Row(equal_height=True):
            with gr.Row(equal_height=True):
                X1 = gr.Number(label="X1", interactive=False)
                X2 = gr.Number(label="X2", interactive=False)
                X3 = gr.Number(label="X3", interactive=False)
                X4 = gr.Number(label="X4", interactive=False)
                S = gr.Number(label="S", interactive=True)
                R = gr.Number(label="R", interactive=True)
            with gr.Column():
                validate_btn = gr.Button("Validate")
            warning_text = gr.Markdown("## Warning!\nIf the validation set does not start right after the calibration set, set S and R values as 0 and add a validation warmup day value above.")
        with gr.Row(equal_height=True):
            with gr.Column(scale = 1):
                validation_output_NSE = gr.Textbox(label="NSE on Validation Set",interactive=False)
                validation_output_KGE = gr.Textbox(label="KGE on Validation Set",interactive=False)
            graph = gr.Plot(label="Hydrograph and Hyteograph")
    
        #Callbacks
        calibrate_btn.click(fn = calibrate_btn_fn, inputs=[calibration_dataset, area, calibration_warmup_days, maxiter, popsize, cpu_count, tolerance, object_function], outputs=[X1, X2, X3, X4, S, R])
        validate_btn.click(fn = validate_btn_fn, inputs=[X1, X2, X3, X4, S, R, validation_dataset, area, validation_warmup_days], outputs=[validation_output_NSE, validation_output_KGE, graph])

        calibration_dataset.change(fn = file_uploaded_fn, inputs=[calibration_dataset], outputs=[calibration_area, calibration_data_start_date, calibration_data_end_date])
        validation_dataset.change(fn = file_uploaded_fn, inputs=[validation_dataset], outputs=[validation_area, validation_data_start_date, validation_data_end_date])
        return GR4J_calibrate_and_validate_tab

def build_calibrate_and_validate_tab(GR4J_calibrate_btn_fn: callable = None, GR4J_validate_btn_fn: callable = None, file_uploaded_fn: callable = None, ):
    with gr.Tab(label="Calibrate and Validate") as calibrate_and_validate:
        build_GR4J_calibrate_and_validate_tab(calibrate_btn_fn=GR4J_calibrate_btn_fn, validate_btn_fn=GR4J_validate_btn_fn, file_uploaded_fn=file_uploaded_fn)
        return calibrate_and_validate

if __name__ == "__main__":
    import callbacks as cb
    import GEE_Exporter as GE
    exporter_service = GE.ExporterService("bratislava-danube-river")
    exporter_service.Authenticate()

    with gr.Blocks(fill_height=True, fill_width=True) as demo:
        sim_tab = build_simulate_tab(simulate_btn_fn=cb.Sim_simulate_btn, file_uploaded_fn=cb.Sim_file_uploaded)
        data_prep_tab = build_data_preparation_tab(session_id="debug", prepare_btn_fn=cb.DataPrep_GR4J_prepare_btn, GR4J_file_uploaded_fn=cb.DataPrep_GR4J_file_uploaded, export_btn_fn=cb.DataPrep_GEE_export_btn, exporter_service=exporter_service, penman_monteith_btn_fn=cb.DataPrep_Penman_Monteith_btn, calculator_file_uploaded_fn=cb.DataPrep_dataset_calculator_file_uploaded, calculater_btn_fn=cb.DataPrep_dataset_calculator_calculate_btn)
        cal_val_tab = build_calibrate_and_validate_tab(GR4J_calibrate_btn_fn=cb.CaV_calibrate_btn, GR4J_validate_btn_fn=cb.CaV_validate_btn, file_uploaded_fn=cb.CaV_file_uploaded)

    try:
        #demo.launch(server_name="0.0.0.0", server_port=7240, max_file_size="100mb")
        demo.launch(max_file_size="100mb")
    finally:
        #exporter_service.deAuthenticate()
        pass