# 🧹 Dead Endpoints and Empty Functions Analysis

## 📊 Summary

- **Total Routes**: 147
- **Template References**: 63
- **JavaScript References**: 3
- **Empty Functions**: 14
- **Dead Endpoints**: 104

## 💀 Dead Endpoints

These endpoints are defined but not referenced in templates or JavaScript:

### strategic.create_company_profile
- **File**: routes/strategic_planning.py
- **Path**: `/strategic/company/new`
- **Methods**: 'GET', 'POST'
- **Function**: `create_company_profile`

### strategic.conduct_market_research
- **File**: routes/strategic_planning.py
- **Path**: `/strategic/company/<int:company_id>/market-research`
- **Methods**: 'POST'
- **Function**: `conduct_market_research`

### strategic.conduct_swot_analysis
- **File**: routes/strategic_planning.py
- **Path**: `/strategic/company/<int:company_id>/swot-analysis`
- **Methods**: 'POST'
- **Function**: `conduct_swot_analysis`

### strategic.generate_strategic_plan
- **File**: routes/strategic_planning.py
- **Path**: `/strategic/company/<int:company_id>/generate-plan/<plan_type>`
- **Methods**: 'POST'
- **Function**: `generate_strategic_plan`

### researchers.get_researchers_api
- **File**: routes/researchers.py
- **Path**: `/api/researchers`
- **Methods**: 'GET'
- **Function**: `get_researchers_api`

### researchers.get_researcher_api
- **File**: routes/researchers.py
- **Path**: `/api/researchers/<orcid_id>`
- **Methods**: 'GET'
- **Function**: `get_researcher_api`

### researchers.search_researchers_api
- **File**: routes/researchers.py
- **Path**: `/api/researchers/search`
- **Methods**: 'POST'
- **Function**: `search_researchers_api`

### research.api_search
- **File**: routes/research.py
- **Path**: `/research/api/search`
- **Methods**: GET
- **Function**: `api_search`

### research.api_status
- **File**: routes/research.py
- **Path**: `/research/api/status`
- **Methods**: GET
- **Function**: `api_status`

### research.api_list
- **File**: routes/research.py
- **Path**: `/research/api/list`
- **Methods**: GET
- **Function**: `api_list`

### research.apply_filters
- **File**: routes/research.py
- **Path**: `/research/filters`
- **Methods**: 'POST'
- **Function**: `apply_filters`

### research.research_funding
- **File**: routes/research.py
- **Path**: `/research/funding`
- **Methods**: 'POST'
- **Function**: `research_funding`

### search.test_search
- **File**: routes/search.py
- **Path**: `/test_search`
- **Methods**: GET
- **Function**: `test_search`

### search.test_rag_search
- **File**: routes/search.py
- **Path**: `/test_rag_search`
- **Methods**: GET
- **Function**: `test_rag_search`

### search.analyze_lead
- **File**: routes/search.py
- **Path**: `/analyze_lead`
- **Methods**: 'POST'
- **Function**: `analyze_lead`

### search.research_leads
- **File**: routes/search.py
- **Path**: `/research_leads`
- **Methods**: 'POST'
- **Function**: `research_leads`

### reports.export_report
- **File**: routes/reports.py
- **Path**: `/export/<report_type>`
- **Methods**: GET
- **Function**: `export_report`

### reports.get_report_stats
- **File**: routes/reports.py
- **Path**: `/api/stats`
- **Methods**: GET
- **Function**: `get_report_stats`

### workflow.quick_search
- **File**: routes/workflow.py
- **Path**: `/workflow/data-in/quick-search`
- **Methods**: 'POST'
- **Function**: `quick_search`

### workflow.research_search
- **File**: routes/workflow.py
- **Path**: `/workflow/data-in/research-search`
- **Methods**: 'POST'
- **Function**: `research_search`

### workflow.upload_documents
- **File**: routes/workflow.py
- **Path**: `/workflow/data-in/upload-documents`
- **Methods**: 'POST'
- **Function**: `upload_documents`

### workflow.ai_research
- **File**: routes/workflow.py
- **Path**: `/workflow/data-in/ai-research`
- **Methods**: 'POST'
- **Function**: `ai_research`

### workflow.web_scraping
- **File**: routes/workflow.py
- **Path**: `/workflow/data-in/web-scraping`
- **Methods**: 'POST'
- **Function**: `web_scraping`

### workflow.analyze_data
- **File**: routes/workflow.py
- **Path**: `/workflow/data-process/analyze`
- **Methods**: 'POST'
- **Function**: `analyze_data`

### workflow.generate_report
- **File**: routes/workflow.py
- **Path**: `/workflow/data-out/generate-report`
- **Methods**: 'POST'
- **Function**: `generate_report`

### workflow.get_progress
- **File**: routes/workflow.py
- **Path**: `/workflow/progress`
- **Methods**: GET
- **Function**: `get_progress`

### workflow.reset_workflow
- **File**: routes/workflow.py
- **Path**: `/workflow/reset`
- **Methods**: 'POST'
- **Function**: `reset_workflow`

### workflow.get_available_data
- **File**: routes/workflow.py
- **Path**: `/workflow/api/available-data`
- **Methods**: GET
- **Function**: `get_available_data`

### workflow.get_workflow_statistics
- **File**: routes/workflow.py
- **Path**: `/workflow/api/statistics`
- **Methods**: GET
- **Function**: `get_workflow_statistics`

### autogpt_control.test_autogpt
- **File**: routes/autogpt_control.py
- **Path**: `/autogpt/test`
- **Methods**: 'POST'
- **Function**: `test_autogpt`

### autogpt_control.analyze_with_autogpt
- **File**: routes/autogpt_control.py
- **Path**: `/autogpt/analyze`
- **Methods**: 'POST'
- **Function**: `analyze_with_autogpt`

### autogpt_control.research_with_autogpt
- **File**: routes/autogpt_control.py
- **Path**: `/autogpt/research`
- **Methods**: 'POST'
- **Function**: `research_with_autogpt`

### autogpt_control.autogpt_status
- **File**: routes/autogpt_control.py
- **Path**: `/autogpt/status`
- **Methods**: GET
- **Function**: `autogpt_status`

### autogpt_control.quick_test_autogpt
- **File**: routes/autogpt_control.py
- **Path**: `/autogpt/quick-test`
- **Methods**: 'POST'
- **Function**: `quick_test_autogpt`

### api_keys.add_api_key
- **File**: routes/api_keys.py
- **Path**: `/api-keys/add`
- **Methods**: 'POST'
- **Function**: `add_api_key`

### api_keys.update_api_key
- **File**: routes/api_keys.py
- **Path**: `/api-keys/<key_id>/update`
- **Methods**: 'POST'
- **Function**: `update_api_key`

### api_keys.delete_api_key
- **File**: routes/api_keys.py
- **Path**: `/api-keys/<key_id>/delete`
- **Methods**: 'DELETE'
- **Function**: `delete_api_key`

### api_keys.get_api_services
- **File**: routes/api_keys.py
- **Path**: `/api-keys/services`
- **Methods**: GET
- **Function**: `get_api_services`

### api_keys.get_service_keys
- **File**: routes/api_keys.py
- **Path**: `/api-keys/services/<service_name>/keys`
- **Methods**: GET
- **Function**: `get_service_keys`

### api_keys.get_usage_statistics
- **File**: routes/api_keys.py
- **Path**: `/api-keys/usage-stats`
- **Methods**: GET
- **Function**: `get_usage_statistics`

### api_keys.test_api_key
- **File**: routes/api_keys.py
- **Path**: `/api-keys/test/<service_name>`
- **Methods**: GET
- **Function**: `test_api_key`

### webscraper.webscraper_home
- **File**: routes/webscraper.py
- **Path**: `/webscraper`
- **Methods**: GET
- **Function**: `webscraper_home`

### webscraper.scrape_urls
- **File**: routes/webscraper.py
- **Path**: `/webscraper/scrape`
- **Methods**: 'POST'
- **Function**: `scrape_urls`

### webscraper.analyze_scraped_content
- **File**: routes/webscraper.py
- **Path**: `/webscraper/analyze`
- **Methods**: 'POST'
- **Function**: `analyze_scraped_content`

### webscraper.get_status
- **File**: routes/webscraper.py
- **Path**: `/webscraper/status`
- **Methods**: GET
- **Function**: `get_status`

### webscraper.test_scraping
- **File**: routes/webscraper.py
- **Path**: `/webscraper/test`
- **Methods**: GET
- **Function**: `test_scraping`

### webscraper.batch_scraping
- **File**: routes/webscraper.py
- **Path**: `/webscraper/batch`
- **Methods**: 'POST'
- **Function**: `batch_scraping`

### config.set_default_research_question
- **File**: routes/config.py
- **Path**: `/config/set_default_research_question`
- **Methods**: 'POST'
- **Function**: `set_default_research_question`

### config.bulk_update_config
- **File**: routes/config.py
- **Path**: `/config/bulk_update`
- **Methods**: 'POST'
- **Function**: `bulk_update_config`

### config.delete_config
- **File**: routes/config.py
- **Path**: `/config/delete/<key_name>`
- **Methods**: 'POST'
- **Function**: `delete_config`

### config.test_config
- **File**: routes/config.py
- **Path**: `/config/test/<key_name>`
- **Methods**: GET
- **Function**: `test_config`

### config.config_status
- **File**: routes/config.py
- **Path**: `/config/status`
- **Methods**: GET
- **Function**: `config_status`

### config.export_config
- **File**: routes/config.py
- **Path**: `/config/export`
- **Methods**: GET
- **Function**: `export_config`

### config.reset_config
- **File**: routes/config.py
- **Path**: `/config/reset`
- **Methods**: 'POST'
- **Function**: `reset_config`

### config.get_config_api
- **File**: routes/config.py
- **Path**: `/api/config`
- **Methods**: 'GET'
- **Function**: `get_config_api`

### config.get_config_key_api
- **File**: routes/config.py
- **Path**: `/api/config/<key_name>`
- **Methods**: 'GET'
- **Function**: `get_config_key_api`

### config.set_config_key_api
- **File**: routes/config.py
- **Path**: `/api/config/<key_name>`
- **Methods**: 'POST'
- **Function**: `set_config_key_api`

### config.delete_config_key_api
- **File**: routes/config.py
- **Path**: `/api/config/<key_name>`
- **Methods**: 'DELETE'
- **Function**: `delete_config_key_api`

### ollama.ollama_search
- **File**: routes/ollama.py
- **Path**: `/ollama_search`
- **Methods**: 'POST'
- **Function**: `ollama_search`

### ollama.advanced_search
- **File**: routes/ollama.py
- **Path**: `/advanced`
- **Methods**: 'POST'
- **Function**: `advanced_search`

### ollama.check_ollama
- **File**: routes/ollama.py
- **Path**: `/check`
- **Methods**: 'POST'
- **Function**: `check_ollama`

### ollama.models_ui
- **File**: routes/ollama.py
- **Path**: `/models`
- **Methods**: GET
- **Function**: `models_ui`

### ollama.download_pdf
- **File**: routes/ollama.py
- **Path**: `/download_pdf`
- **Methods**: 'POST'
- **Function**: `download_pdf`

### ollama.download_multiple_pdfs
- **File**: routes/ollama.py
- **Path**: `/download_multiple`
- **Methods**: 'POST'
- **Function**: `download_multiple_pdfs`

### ollama.download_pdf_enhanced
- **File**: routes/ollama.py
- **Path**: `/download_pdf_enhanced`
- **Methods**: 'POST'
- **Function**: `download_pdf_enhanced`

### ollama.batch_download
- **File**: routes/ollama.py
- **Path**: `/batch_download`
- **Methods**: 'POST'
- **Function**: `batch_download`

### ollama.get_mirror_status
- **File**: routes/ollama.py
- **Path**: `/mirror_status`
- **Methods**: GET
- **Function**: `get_mirror_status`

### ollama.get_downloaded_files
- **File**: routes/ollama.py
- **Path**: `/downloaded_files`
- **Methods**: GET
- **Function**: `get_downloaded_files`

### ollama.view_downloads
- **File**: routes/ollama.py
- **Path**: `/view_downloads`
- **Methods**: GET
- **Function**: `view_downloads`

### ollama.download_file
- **File**: routes/ollama.py
- **Path**: `/download/<path:file_path>`
- **Methods**: GET
- **Function**: `download_file`

### ollama.send_pdf_to_workshop
- **File**: routes/ollama.py
- **Path**: `/send_pdf_to_workshop`
- **Methods**: 'POST'
- **Function**: `send_pdf_to_workshop`

### ollama.ollama_status
- **File**: routes/ollama.py
- **Path**: `/ollama_status`
- **Methods**: GET
- **Function**: `ollama_status`

### ollama.send_to_workshop
- **File**: routes/ollama.py
- **Path**: `/send_to_workshop`
- **Methods**: 'POST'
- **Function**: `send_to_workshop`

### lead_workshop.create_project
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/create-project`
- **Methods**: 'POST'
- **Function**: `create_project`

### lead_workshop.analyze_leads
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/analyze-leads`
- **Methods**: 'POST'
- **Function**: `analyze_leads`

### lead_workshop.delete_workshop_leads
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/delete-workshop-leads`
- **Methods**: 'POST'
- **Function**: `delete_workshop_leads`

### lead_workshop.delete_analyses
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/delete-analyses`
- **Methods**: 'POST'
- **Function**: `delete_analyses`

### lead_workshop.api_status
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/api/status`
- **Methods**: GET
- **Function**: `api_status`

### lead_workshop.export_project_pdf
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/export-pdf/<int:project_id>`
- **Methods**: GET
- **Function**: `export_project_pdf`

### lead_workshop.export_project_markdown
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/export-markdown/<int:project_id>`
- **Methods**: GET
- **Function**: `export_project_markdown`

### lead_workshop.generate_custom_pdf
- **File**: routes/lead_workshop.py
- **Path**: `/lead-workshop/generate-custom-pdf/<int:project_id>`
- **Methods**: 'POST'
- **Function**: `generate_custom_pdf`

### dashboard.api_stats
- **File**: routes/dashboard.py
- **Path**: `/api/stats`
- **Methods**: GET
- **Function**: `api_stats`

### dashboard.api_activity
- **File**: routes/dashboard.py
- **Path**: `/api/activity`
- **Methods**: GET
- **Function**: `api_activity`

### dashboard.api_system_status
- **File**: routes/dashboard.py
- **Path**: `/api/system-status`
- **Methods**: GET
- **Function**: `api_system_status`

### rag.rag_search_form
- **File**: routes/rag_routes.py
- **Path**: `/search`
- **Methods**: 'GET'
- **Function**: `rag_search_form`

### rag.rag_status
- **File**: routes/rag_routes.py
- **Path**: `/status`
- **Methods**: 'GET'
- **Function**: `rag_status`

### rag.rag_health
- **File**: routes/rag_routes.py
- **Path**: `/health`
- **Methods**: 'GET'
- **Function**: `rag_health`

### leads.download_links
- **File**: routes/leads.py
- **Path**: `/download_links`
- **Methods**: GET
- **Function**: `download_links`

### leads.bulk_delete_leads
- **File**: routes/leads.py
- **Path**: `/bulk-delete`
- **Methods**: 'POST'
- **Function**: `bulk_delete_leads`

### leads.leads_by_source
- **File**: routes/leads.py
- **Path**: `/leads_by_source/<source>`
- **Methods**: GET
- **Function**: `leads_by_source`

### leads.get_leads_api
- **File**: routes/leads.py
- **Path**: `/api/leads`
- **Methods**: 'GET'
- **Function**: `get_leads_api`

### leads.get_lead_api
- **File**: routes/leads.py
- **Path**: `/api/leads/<int:lead_id>`
- **Methods**: 'GET'
- **Function**: `get_lead_api`

### leads.update_lead_api
- **File**: routes/leads.py
- **Path**: `/api/leads/<int:lead_id>`
- **Methods**: 'PUT'
- **Function**: `update_lead_api`

### leads.delete_lead_api
- **File**: routes/leads.py
- **Path**: `/api/leads/<int:lead_id>`
- **Methods**: 'DELETE'
- **Function**: `delete_lead_api`

### leads.export_leads_api
- **File**: routes/leads.py
- **Path**: `/api/leads/export`
- **Methods**: 'GET'
- **Function**: `export_leads_api`

### unified_search.search_stats
- **File**: routes/unified_search.py
- **Path**: `/search_stats`
- **Methods**: GET
- **Function**: `search_stats`

### unified_search.clear_cache
- **File**: routes/unified_search.py
- **Path**: `/clear_cache`
- **Methods**: 'POST'
- **Function**: `clear_cache`

### progress.get_progress
- **File**: routes/progress.py
- **Path**: `/progress/<operation_id>`
- **Methods**: GET
- **Function**: `get_progress`

### progress.stream_progress
- **File**: routes/progress.py
- **Path**: `/progress/<operation_id>/stream`
- **Methods**: GET
- **Function**: `stream_progress`

### progress.get_active_operations
- **File**: routes/progress.py
- **Path**: `/progress/active`
- **Methods**: GET
- **Function**: `get_active_operations`

### progress.get_recent_operations
- **File**: routes/progress.py
- **Path**: `/progress/recent`
- **Methods**: GET
- **Function**: `get_recent_operations`

### progress.cleanup_old_operations
- **File**: routes/progress.py
- **Path**: `/progress/cleanup`
- **Methods**: 'POST'
- **Function**: `cleanup_old_operations`

### progress.cancel_operation
- **File**: routes/progress.py
- **Path**: `/progress/<operation_id>/cancel`
- **Methods**: 'POST'
- **Function**: `cancel_operation`

### progress.get_operation_details
- **File**: routes/progress.py
- **Path**: `/progress/<operation_id>/details`
- **Methods**: GET
- **Function**: `get_operation_details`

## 🔍 Empty/Stub Functions

These functions are empty or contain only TODO comments:

### EMPTY Functions

- **home** in `test_minimal_app.py:14`
- **health** in `test_minimal_app.py:18`
- **not_found_error** in `app.py:440`
- **internal_error** in `app.py:444`
- **test_api_function** in `test_improvements.py:123`
- **__enter__** in `utils/error_handler.py:319`
- **save_lead** in `models/database.py:1024`
- **get_all_leads** in `models/database.py:1031`
- **get_leads_by_source** in `models/database.py:1034`
- **update_lead** in `models/database.py:1037`
- **delete_lead** in `models/database.py:1046`
- **save_search_history** in `models/database.py:1049`
- **get_search_history** in `models/database.py:1052`
- **get_lead_count** in `models/database.py:1055`

## 📊 Route Analysis by Blueprint

### strategic_bp
- **Total Routes**: 6

✅ `strategic_dashboard` - `/strategic`
💀 `create_company_profile` - `/strategic/company/new`
✅ `view_company_profile` - `/strategic/company/<int:company_id>`
💀 `conduct_market_research` - `/strategic/company/<int:company_id>/market-research`
💀 `conduct_swot_analysis` - `/strategic/company/<int:company_id>/swot-analysis`
💀 `generate_strategic_plan` - `/strategic/company/<int:company_id>/generate-plan/<plan_type>`

### researchers_bp
- **Total Routes**: 9

✅ `researchers_home` - `/researchers`
✅ `search_researchers_route` - `/researchers/search`
✅ `researcher_profile` - `/researchers/<orcid_id>`
✅ `lookup_researcher_funding` - `/researchers/<orcid_id>/funding`
✅ `lookup_researcher_publications` - `/researchers/<orcid_id>/publications`
✅ `researcher_database` - `/researchers/database`
💀 `get_researchers_api` - `/api/researchers`
💀 `get_researcher_api` - `/api/researchers/<orcid_id>`
💀 `search_researchers_api` - `/api/researchers/search`

### research_bp
- **Total Routes**: 8

✅ `research_home` - `/research`
✅ `search_research` - `/research/search`
💀 `api_search` - `/research/api/search`
✅ `project_details` - `/research/project/<source>/<project_id>`
💀 `api_status` - `/research/api/status`
💀 `api_list` - `/research/api/list`
💀 `apply_filters` - `/research/filters`
💀 `research_funding` - `/research/funding`

### search_bp
- **Total Routes**: 7

✅ `perform_search` - `/search`
✅ `perform_search_ajax` - `/search_ajax`
✅ `search_form` - `/search_form`
💀 `test_search` - `/test_search`
💀 `test_rag_search` - `/test_rag_search`
💀 `analyze_lead` - `/analyze_lead`
💀 `research_leads` - `/research_leads`

### reports_bp
- **Total Routes**: 6

✅ `reports_home` - `/`
✅ `market_analysis_report` - `/market-analysis`
✅ `lead_analysis_report` - `/lead-analysis`
✅ `executive_summary_report` - `/executive-summary`
💀 `export_report` - `/export/<report_type>`
💀 `get_report_stats` - `/api/stats`

### workflow_bp
- **Total Routes**: 15

✅ `workflow_dashboard` - `/workflow`
✅ `data_in_dashboard` - `/workflow/data-in`
✅ `data_process_dashboard` - `/workflow/data-process`
✅ `data_out_dashboard` - `/workflow/data-out`
💀 `quick_search` - `/workflow/data-in/quick-search`
💀 `research_search` - `/workflow/data-in/research-search`
💀 `upload_documents` - `/workflow/data-in/upload-documents`
💀 `ai_research` - `/workflow/data-in/ai-research`
💀 `web_scraping` - `/workflow/data-in/web-scraping`
💀 `analyze_data` - `/workflow/data-process/analyze`
💀 `generate_report` - `/workflow/data-out/generate-report`
💀 `get_progress` - `/workflow/progress`
💀 `reset_workflow` - `/workflow/reset`
💀 `get_available_data` - `/workflow/api/available-data`
💀 `get_workflow_statistics` - `/workflow/api/statistics`

### autogpt_control_bp
- **Total Routes**: 6

✅ `control_panel` - `/autogpt/control`
💀 `test_autogpt` - `/autogpt/test`
💀 `analyze_with_autogpt` - `/autogpt/analyze`
💀 `research_with_autogpt` - `/autogpt/research`
💀 `autogpt_status` - `/autogpt/status`
💀 `quick_test_autogpt` - `/autogpt/quick-test`

### api_keys_bp
- **Total Routes**: 8

✅ `api_keys_dashboard` - `/api-keys`
💀 `add_api_key` - `/api-keys/add`
💀 `update_api_key` - `/api-keys/<key_id>/update`
💀 `delete_api_key` - `/api-keys/<key_id>/delete`
💀 `get_api_services` - `/api-keys/services`
💀 `get_service_keys` - `/api-keys/services/<service_name>/keys`
💀 `get_usage_statistics` - `/api-keys/usage-stats`
💀 `test_api_key` - `/api-keys/test/<service_name>`

### webscraper_bp
- **Total Routes**: 6

💀 `webscraper_home` - `/webscraper`
💀 `scrape_urls` - `/webscraper/scrape`
💀 `analyze_scraped_content` - `/webscraper/analyze`
💀 `get_status` - `/webscraper/status`
💀 `test_scraping` - `/webscraper/test`
💀 `batch_scraping` - `/webscraper/batch`

### config_bp
- **Total Routes**: 13

✅ `config_home` - `/config`
💀 `set_default_research_question` - `/config/set_default_research_question`
✅ `update_config` - `/config/update`
💀 `bulk_update_config` - `/config/bulk_update`
💀 `delete_config` - `/config/delete/<key_name>`
💀 `test_config` - `/config/test/<key_name>`
💀 `config_status` - `/config/status`
💀 `export_config` - `/config/export`
💀 `reset_config` - `/config/reset`
💀 `get_config_api` - `/api/config`
💀 `get_config_key_api` - `/api/config/<key_name>`
💀 `set_config_key_api` - `/api/config/<key_name>`
💀 `delete_config_key_api` - `/api/config/<key_name>`

### ollama_bp
- **Total Routes**: 18

💀 `ollama_home` - `/`
💀 `ollama_search` - `/ollama_search`
💀 `advanced_search` - `/advanced`
💀 `check_ollama` - `/check`
💀 `models_ui` - `/models`
✅ `set_model` - `/set_model`
💀 `download_pdf` - `/download_pdf`
💀 `download_multiple_pdfs` - `/download_multiple`
💀 `download_pdf_enhanced` - `/download_pdf_enhanced`
💀 `batch_download` - `/batch_download`
💀 `get_mirror_status` - `/mirror_status`
💀 `get_downloaded_files` - `/downloaded_files`
💀 `view_downloads` - `/view_downloads`
💀 `download_file` - `/download/<path:file_path>`
💀 `send_pdf_to_workshop` - `/send_pdf_to_workshop`
💀 `ollama_status` - `/ollama_status`
✅ `ollama_models` - `/ollama_models`
💀 `send_to_workshop` - `/send_to_workshop`

### lead_workshop_bp
- **Total Routes**: 12

✅ `lead_workshop_home` - `/lead-workshop`
💀 `create_project` - `/lead-workshop/create-project`
💀 `analyze_leads` - `/lead-workshop/analyze-leads`
💀 `delete_workshop_leads` - `/lead-workshop/delete-workshop-leads`
✅ `view_project` - `/lead-workshop/project/<int:project_id>`
💀 `delete_analyses` - `/lead-workshop/delete-analyses`
✅ `update_analysis` - `/lead-workshop/update-analysis`
💀 `api_status` - `/lead-workshop/api/status`
💀 `export_project_pdf` - `/lead-workshop/export-pdf/<int:project_id>`
💀 `export_project_markdown` - `/lead-workshop/export-markdown/<int:project_id>`
✅ `edit_report` - `/lead-workshop/edit-report/<int:project_id>`
💀 `generate_custom_pdf` - `/lead-workshop/generate-custom-pdf/<int:project_id>`

### dashboard_bp
- **Total Routes**: 4

✅ `index` - `/`
💀 `api_stats` - `/api/stats`
💀 `api_activity` - `/api/activity`
💀 `api_system_status` - `/api/system-status`

### rag_bp
- **Total Routes**: 4

💀 `rag_search_form` - `/search`
💀 `rag_status` - `/status`
✅ `rag_stats` - `/stats`
💀 `rag_health` - `/health`

### leads_bp
- **Total Routes**: 14

✅ `show_leads` - `/`
✅ `export_to_excel` - `/export`
✅ `export_to_csv` - `/export/csv`
💀 `download_links` - `/download_links`
✅ `delete_lead` - `/delete/<int:lead_id>`
💀 `bulk_delete_leads` - `/bulk-delete`
💀 `leads_by_source` - `/leads_by_source/<source>`
✅ `summarize_lead` - `/summarize/<int:lead_id>`
✅ `summarize_lead_ajax` - `/summarize_ajax/<int:lead_id>`
💀 `get_leads_api` - `/api/leads`
💀 `get_lead_api` - `/api/leads/<int:lead_id>`
💀 `update_lead_api` - `/api/leads/<int:lead_id>`
💀 `delete_lead_api` - `/api/leads/<int:lead_id>`
💀 `export_leads_api` - `/api/leads/export`

### unified_search_bp
- **Total Routes**: 4

✅ `unified_search` - `/unified_search`
✅ `unified_search_form` - `/unified_search_form`
💀 `search_stats` - `/search_stats`
💀 `clear_cache` - `/clear_cache`

### progress_bp
- **Total Routes**: 7

💀 `get_progress` - `/progress/<operation_id>`
💀 `stream_progress` - `/progress/<operation_id>/stream`
💀 `get_active_operations` - `/progress/active`
💀 `get_recent_operations` - `/progress/recent`
💀 `cleanup_old_operations` - `/progress/cleanup`
💀 `cancel_operation` - `/progress/<operation_id>/cancel`
💀 `get_operation_details` - `/progress/<operation_id>/details`
