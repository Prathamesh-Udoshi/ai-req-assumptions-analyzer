"""
Suggestion Generation Module

This module generates actionable clarifying questions based on detected
ambiguity and assumption issues. Each question helps requirement authors
provide the specific details needed for effective test automation.
"""

from typing import List, Dict, Any, Union

from .ambiguity_detector import AmbiguityIssue
from .assumption_detector import AssumptionIssue


class SuggestionGenerator:
    """
    Generates clarifying questions for detected issues.

    Provides specific, actionable questions that help requirement authors
    eliminate ambiguity and document assumptions explicitly.
    """

    def __init__(self):
        """Initialize the suggestion generator."""
        # Define suggestion templates for different issue types
        self.ambiguity_suggestions = {
            "Subjective term": {
                # Performance terms
                "fast": ["What is the acceptable response time in seconds?", "What is the maximum latency threshold?", "How does this compare to industry standards?"],
                "slow": ["What is the maximum acceptable response time?", "What performance degradation is tolerable?", "How does this impact user experience?"],
                "quick": ["What is the expected response time in milliseconds?", "What constitutes 'quick' for this operation?", "How does this compare to similar operations?"],
                "rapid": ["What is the required speed in operations per second?", "What is the acceptable throughput rate?", "How does this impact system resources?"],
                "instant": ["What is the maximum acceptable delay in milliseconds?", "What is the expected immediate response time?", "How does this affect real-time requirements?"],
                "immediate": ["What is the maximum delay before response?", "What constitutes immediate action?", "How does this impact user expectations?"],
                "speedy": ["What is the required processing speed?", "What performance metrics define 'speedy'?", "How does this compare to baseline performance?"],
                "swift": ["What is the expected execution time?", "What defines swift completion?", "How does this impact workflow efficiency?"],
                "brisk": ["What is the required briskness threshold?", "What performance indicators are expected?", "How does this affect user satisfaction?"],
                "sluggish": ["What is the unacceptable slowness threshold?", "What performance issues are tolerable?", "How does this impact system usability?"],
                "laggy": ["What is the maximum acceptable lag time?", "What lag is considered problematic?", "How does this affect interactive operations?"],
                "smooth": ["What performance characteristics define smoothness?", "What is the acceptable jitter or variance?", "How does this impact user experience quality?"],
                "responsive": ["What is the required response time for user interactions?", "What responsiveness metrics are expected?", "How does this compare to similar applications?"],
                "snappy": ["What is the expected snappiness threshold?", "What defines crisp performance?", "How does this impact perceived performance?"],
                "nimble": ["What agility requirements are expected?", "What defines nimble operation?", "How does this affect system adaptability?"],
                "agile": ["What is the required agility in response?", "What defines agile performance?", "How does this impact change management?"],
                "zippy": ["What is the expected zippy performance threshold?", "What defines energetic response?", "How does this impact user engagement?"],
                "blazing": ["What is the blazing speed requirement?", "What defines blazingly fast?", "How does this impact resource utilization?"],
                "lightning": ["What is the lightning-fast requirement?", "What defines lightning speed?", "How does this impact system architecture?"],
                "superfast": ["What is the superfast performance threshold?", "What defines exceptional speed?", "How does this impact scalability?"],
                "ultrafast": ["What is the ultrafast requirement?", "What defines ultra-fast operation?", "How does this impact real-time processing?"],
                "fluid": ["What performance characteristics define fluidity?", "What is the acceptable transition smoothness?", "How does this impact animation requirements?"],
                "seamless": ["What defines seamless operation?", "What integration smoothness is expected?", "How does this impact user workflow?"],
                "effortless": ["What defines effortless interaction?", "What ease-of-use metrics are expected?", "How does this impact accessibility?"],
                "default": ["What specific, measurable criteria define this subjective term?", "What quantitative metrics should be used?", "How should this be measured in testing?"]
            },
            "Weak modality": {
                "should": ["Is this a mandatory requirement or optional?", "Under what conditions must this occur?", "What happens if this requirement is not met?"],
                "could": ["Under what specific conditions should this behavior occur?", "What factors determine when this is appropriate?", "What is the alternative when this cannot occur?"],
                "might": ["When and under what conditions should this occur?", "What probability threshold triggers this behavior?", "What is the expected behavior when conditions are not met?"],
                "may": ["What specific conditions determine when this behavior occurs?", "What permissions or states enable this functionality?", "What happens in the default case?"],
                "can": ["What specific capabilities enable this functionality?", "What conditions must be met for this to be possible?", "What limitations prevent this from occurring?"],
                "if possible": ["What should happen if this is not possible?", "What are the fallback behaviors?", "What conditions determine possibility?"],
                "when possible": ["What takes precedence when this is not possible?", "What are the timing constraints?", "What conditions enable this possibility?"],
                "as needed": ["What triggers determine when this is needed?", "What conditions indicate necessity?", "How frequently should this occur?"],
                "when necessary": ["What conditions make this necessary?", "What criteria determine necessity?", "What happens when it's not necessary?"],
                "depending on": ["What specific factors determine the behavior?", "What are the decision criteria?", "How should the system choose between options?"],
                "in case of": ["What specific conditions trigger this behavior?", "What are the error or exceptional scenarios?", "What is the expected frequency of these cases?"],
                "provided that": ["What specific conditions must be satisfied?", "What prerequisites are required?", "What happens when conditions are not met?"],
                "ideally": ["What is the minimum acceptable behavior if ideal is not achieved?", "What are the priority levels?", "What trade-offs are acceptable?"],
                "preferably": ["What is the alternative if preference cannot be satisfied?", "What are the acceptable fallbacks?", "What determines preference priority?"],
                "would like": ["What is the minimum viable behavior?", "What are the nice-to-have vs. must-have requirements?", "What happens without this feature?"],
                "possibly": ["What probability makes this possible?", "What conditions enable this possibility?", "What is the expected likelihood?"],
                "potentially": ["What factors could enable this?", "What are the potential scenarios?", "What conditions trigger this potential?"],
                "feasible": ["What specific constraints determine feasibility?", "What resources are required?", "What makes this infeasible?"],
                "viable": ["What viability criteria must be met?", "What sustainability requirements exist?", "What makes this non-viable?"],
                "practicable": ["What practical constraints apply?", "What implementation challenges exist?", "What makes this impracticable?"],
                "achievable": ["What achievement criteria are defined?", "What success metrics apply?", "What makes this unachievable?"],
                "attainable": ["What attainment conditions exist?", "What accessibility requirements apply?", "What makes this unattainable?"],
                "realizable": ["What realization constraints exist?", "What implementation requirements apply?", "What makes this unrealizable?"],
                "doable": ["What specific capabilities are required?", "What skill or resource requirements exist?", "What makes this undoable?"],
                "workable": ["What workability criteria apply?", "What operational requirements exist?", "What makes this unworkable?"],
                "default": ["What specific conditions determine when this occurs?", "What are the exact requirements?", "How should this be implemented?"]
            },
            "Undefined reference": {
                "it": ["What specific element, component, or data does 'it' refer to?", "Can you identify the exact referent?", "What should replace this pronoun?"],
                "this": ["What specific element, component, or data does 'this' refer to?", "Can you clarify the exact referent?", "What specific item is being referenced?"],
                "that": ["What specific element, component, or data does 'that' refer to?", "Can you identify the exact referent?", "What should replace this reference?"],
                "these": ["What specific elements or components do 'these' refer to?", "Can you list the exact referents?", "What specific items are being referenced?"],
                "those": ["What specific elements or components do 'those' refer to?", "Can you identify the exact referents?", "What specific items should be referenced?"],
                "them": ["What specific elements or components do 'them' refer to?", "Can you clarify what 'them' represents?", "What specific items are being acted upon?"],
                "they": ["What specific elements or components do 'they' refer to?", "Can you identify who or what 'they' represents?", "What specific actors are involved?"],
                "their": ["What specific elements or components do 'their' refer to?", "Can you clarify the ownership relationship?", "Whose attributes or possessions are being referenced?"],
                "theirs": ["What specific elements or components do 'theirs' refer to?", "Can you clarify what belongs to them?", "What specific ownership is being referenced?"],
                "itself": ["What specific element or component does 'itself' refer to?", "Can you clarify the reflexive reference?", "What is the self-referential element?"],
                "themselves": ["What specific elements or components do 'themselves' refer to?", "Can you clarify the reflexive reference?", "What are the self-referential elements?"],
                "one": ["What specific element or component does 'one' refer to?", "Can you clarify this generic reference?", "What specific instance is being referenced?"],
                "ones": ["What specific elements or components do 'ones' refer to?", "Can you clarify these generic references?", "What specific instances are being referenced?"],
                "such": ["What specific characteristics or examples does 'such' refer to?", "Can you provide concrete examples?", "What specific criteria define 'such'?"],
                "same": ["What specific element or standard does 'same' refer to?", "Can you clarify what should be identical?", "What specific consistency requirements exist?"],
                "other": ["What specific alternative or different element does 'other' refer to?", "Can you clarify the contrast?", "What specific differentiation is required?"],
                "others": ["What specific alternative or different elements do 'others' refer to?", "Can you clarify the contrast?", "What specific differentiation is required?"],
                "another": ["What specific alternative element does 'another' refer to?", "Can you clarify what other option?", "What specific alternative is being considered?"],
                "each": ["What specific elements does 'each' refer to?", "Can you clarify the scope of iteration?", "What specific items should be processed individually?"],
                "every": ["What specific elements does 'every' refer to?", "Can you clarify the universal scope?", "What specific items should be included?"],
                "all": ["What specific elements does 'all' refer to?", "Can you clarify the complete scope?", "What specific items should be included?"],
                "some": ["What specific elements does 'some' refer to?", "Can you clarify which subset?", "What specific items are being referenced?"],
                "any": ["What specific elements does 'any' refer to?", "Can you clarify the selection criteria?", "What specific items could be chosen?"],
                "none": ["What specific elements does 'none' refer to?", "Can you clarify the exclusion criteria?", "What specific items should be excluded?"],
                "both": ["What specific pair of elements does 'both' refer to?", "Can you clarify the dual reference?", "What specific items should be included together?"],
                "either": ["What specific alternative elements does 'either' refer to?", "Can you clarify the choice?", "What specific options are available?"],
                "the system": ["Which specific system or subsystem is being referenced?", "Can you identify the exact system?", "What specific system components are involved?"],
                "the application": ["Which specific application is being referenced?", "Can you identify the exact application?", "What specific application features are involved?"],
                "the software": ["Which specific software component is being referenced?", "Can you identify the exact software?", "What specific software functionality is involved?"],
                "the platform": ["Which specific platform is being referenced?", "Can you identify the exact platform?", "What specific platform capabilities are involved?"],
                "the component": ["Which specific component is being referenced?", "Can you identify the exact component?", "What specific component functionality is involved?"],
                "the module": ["Which specific module is being referenced?", "Can you identify the exact module?", "What specific module functionality is involved?"],
                "the service": ["Which specific service is being referenced?", "Can you identify the exact service?", "What specific service functionality is involved?"],
                "the interface": ["Which specific interface is being referenced?", "Can you identify the exact interface?", "What specific interface elements are involved?"],
                "the api": ["Which specific API is being referenced?", "Can you identify the exact API?", "What specific API endpoints are involved?"],
                "the database": ["Which specific database is being referenced?", "Can you identify the exact database?", "What specific database tables are involved?"],
                "the server": ["Which specific server is being referenced?", "Can you identify the exact server?", "What specific server functionality is involved?"],
                "the client": ["Which specific client is being referenced?", "Can you identify the exact client?", "What specific client functionality is involved?"],
                "the backend": ["Which specific backend is being referenced?", "Can you identify the exact backend?", "What specific backend functionality is involved?"],
                "the frontend": ["Which specific frontend is being referenced?", "Can you identify the exact frontend?", "What specific frontend elements are involved?"],
                "the middleware": ["Which specific middleware is being referenced?", "Can you identify the exact middleware?", "What specific middleware functionality is involved?"],
                "the framework": ["Which specific framework is being referenced?", "Can you identify the exact framework?", "What specific framework capabilities are involved?"],
                "the library": ["Which specific library is being referenced?", "Can you identify the exact library?", "What specific library functionality is involved?"],
                "the tool": ["Which specific tool is being referenced?", "Can you identify the exact tool?", "What specific tool functionality is involved?"],
                "the utility": ["Which specific utility is being referenced?", "Can you identify the exact utility?", "What specific utility functionality is involved?"],
                "the engine": ["Which specific engine is being referenced?", "Can you identify the exact engine?", "What specific engine functionality is involved?"],
                "the user": ["What type of user or user role is being referenced?", "Can you identify the specific user characteristics?", "What specific user permissions are involved?"],
                "the customer": ["What type of customer is being referenced?", "Can you identify the specific customer characteristics?", "What specific customer requirements are involved?"],
                "the client": ["What type of client is being referenced?", "Can you identify the specific client characteristics?", "What specific client requirements are involved?"],
                "the admin": ["What type of administrator is being referenced?", "Can you identify the specific admin role?", "What specific admin permissions are involved?"],
                "the manager": ["What type of manager is being referenced?", "Can you identify the specific manager role?", "What specific manager permissions are involved?"],
                "the operator": ["What type of operator is being referenced?", "Can you identify the specific operator role?", "What specific operator permissions are involved?"],
                "the visitor": ["What type of visitor is being referenced?", "Can you identify the specific visitor characteristics?", "What specific visitor permissions are involved?"],
                "the data": ["What specific data is being referenced?", "Can you identify the exact data elements?", "What specific data structure is involved?"],
                "the information": ["What specific information is being referenced?", "Can you identify the exact information content?", "What specific information format is involved?"],
                "the content": ["What specific content is being referenced?", "Can you identify the exact content elements?", "What specific content type is involved?"],
                "the record": ["What specific record is being referenced?", "Can you identify the exact record structure?", "What specific record fields are involved?"],
                "the entry": ["What specific entry is being referenced?", "Can you identify the exact entry format?", "What specific entry fields are involved?"],
                "the item": ["What specific item is being referenced?", "Can you identify the exact item characteristics?", "What specific item properties are involved?"],
                "the object": ["What specific object is being referenced?", "Can you identify the exact object type?", "What specific object properties are involved?"],
                "the element": ["What specific element is being referenced?", "Can you identify the exact element type?", "What specific element attributes are involved?"],
                "default": ["What specific element or component is being referenced?", "Can you identify the exact referent?", "What specific item should replace this reference?"]
            },
            "Non-testable statement": {
                "default": ["What specific, measurable criteria define success?", "What quantitative metrics can be used to verify this?", "How should this be tested in practice?", "What specific acceptance criteria apply?", "What observable behavior confirms this requirement?"]
            }
        }

        self.assumption_suggestions = {
            "Environment": {
                "UI interaction": ["Which browser(s), device(s), and operating system(s) should be supported?", "What are the target environment specifications?", "What platforms must this work on?"],
                "browsers": ["Which specific browsers and versions must be supported?", "What are the browser compatibility requirements?", "Which browser features are required?"],
                "devices": ["Which specific devices and screen sizes must be supported?", "What are the device compatibility requirements?", "What device capabilities are required?"],
                "operating_systems": ["Which specific operating systems and versions must be supported?", "What are the OS compatibility requirements?", "What OS features are required?"],
                "network": ["What network conditions must be supported?", "What are the connectivity requirements?", "What network speeds and reliability are expected?"],
                "display": ["What display resolutions and types must be supported?", "What are the visual requirements?", "What accessibility features are needed?"],
                "databases": ["Which specific database systems must be supported?", "What are the database compatibility requirements?", "What database features are required?"],
                "apis": ["Which specific APIs and protocols must be supported?", "What are the API compatibility requirements?", "What authentication methods are required?"],
                "cloud_providers": ["Which cloud platforms must be supported?", "What are the cloud deployment requirements?", "What cloud services are required?"],
                "default": ["What is the target environment for this requirement?", "What environmental conditions must be met?", "What infrastructure is required?"]
            },
            "Data": {
                "user_exists": ["What specific test user accounts should be available?", "What user profiles are needed for testing?", "What user data should be pre-populated?"],
                "credentials_exist": ["What specific user credentials should be prepared?", "What authentication data is required?", "What login information should be available?"],
                "form_filled": ["What specific data should be pre-filled in forms?", "What test data scenarios are needed?", "What form data combinations should be tested?"],
                "data_entered": ["What specific input data should be prepared?", "What test data sets are required?", "What data entry scenarios should be tested?"],
                "record_exists": ["What specific database records should exist?", "What test data should be in the database?", "What record states should be available?"],
                "data_exists": ["What specific test data should be available?", "What data sets are required for testing?", "What data conditions should exist?"],
                "page_exists": ["What specific pages should be available?", "What page content should exist?", "What page states should be testable?"],
                "resource_exists": ["What specific resources should be available?", "What resource states should exist?", "What resource data should be prepared?"],
                "content_exists": ["What specific content should be available?", "What content states should exist?", "What content variations should be tested?"],
                "file_exists": ["What specific files should be available?", "What file types and sizes should exist?", "What file content should be prepared?"],
                "recipient_exists": ["What specific message recipients should exist?", "What recipient data should be available?", "What recipient scenarios should be tested?"],
                "sender_exists": ["What specific message senders should exist?", "What sender data should be available?", "What sender scenarios should be tested?"],
                "task_exists": ["What specific tasks should be available?", "What task states should exist?", "What task data should be prepared?"],
                "item_exists": ["What specific items should be available?", "What item states should exist?", "What item variations should be tested?"],
                "issue_exists": ["What specific issues should be available?", "What issue states should exist?", "What issue scenarios should be tested?"],
                "default": ["What test data or records need to be prepared?", "What data preconditions are required?", "What data states should exist?"]
            },
            "State": {
                "user_logged_in": ["Should the user be pre-authenticated for testing?", "What authentication state is required?", "What login session should exist?"],
                "permissions_granted": ["What specific user role and permissions are required?", "What authorization level is needed?", "What access rights should be configured?"],
                "condition_exists": ["What specific preconditions must be met?", "What system state is required?", "What conditions should trigger this behavior?"],
                "error_trigger": ["How can specific error conditions be reliably reproduced?", "What error states should be testable?", "What failure scenarios need to be triggered?"],
                "failure_condition": ["What conditions will cause failure scenarios?", "What error states should exist?", "What failure paths should be tested?"],
                "admin_role": ["What admin user roles should be available?", "What administrative permissions are needed?", "What admin access levels should exist?"],
                "manager_role": ["What manager user roles should be available?", "What management permissions are needed?", "What manager access levels should exist?"],
                "user_role": ["What regular user roles should be available?", "What user permissions are needed?", "What user access levels should exist?"],
                "account_active": ["What user account states should be available?", "What account activation scenarios should exist?", "What account statuses should be testable?"],
                "form_valid": ["What form validation states should exist?", "What validation scenarios should be tested?", "What form completion states are required?"],
                "space_available": ["What storage space should be available?", "What disk space requirements exist?", "What capacity limits should be tested?"],
                "container_exists": ["What parent containers should exist?", "What container states should be available?", "What container hierarchies are needed?"],
                "position_valid": ["What valid insertion positions should exist?", "What positioning constraints apply?", "What location states should be testable?"],
                "list_exists": ["What lists or collections should exist?", "What list states should be available?", "What list content should be prepared?"],
                "search_index_exists": ["What search indexes should be populated?", "What searchable content should exist?", "What search states should be available?"],
                "sortable_data_exists": ["What sortable data sets should exist?", "What sorting scenarios should be available?", "What data ordering should be testable?"],
                "searchable_content_exists": ["What searchable content should exist?", "What search scenarios should be available?", "What content indexing should be prepared?"],
                "query_engine_available": ["What query processing should be available?", "What search engine states should exist?", "What query capabilities should be configured?"],
                "searchable_items_exist": ["What items should be searchable?", "What search target states should exist?", "What searchable object scenarios should be prepared?"],
                "lookup_table_exists": ["What reference data should be available?", "What lookup table content should exist?", "What reference data states should be prepared?"],
                "data_source_available": ["What data sources should be accessible?", "What data connection states should exist?", "What data availability scenarios should be tested?"],
                "api_endpoint_available": ["What API endpoints should be operational?", "What API states should exist?", "What service availability scenarios should be tested?"],
                "resource_accessible": ["What resources should be accessible?", "What resource availability states should exist?", "What access scenarios should be tested?"],
                "verification_criteria_defined": ["What verification criteria should be configured?", "What validation rules should exist?", "What verification scenarios should be prepared?"],
                "check_criteria_defined": ["What check criteria should be configured?", "What validation rules should exist?", "What checking scenarios should be prepared?"],
                "validation_rules_defined": ["What validation rules should be configured?", "What data validation scenarios should exist?", "What validation states should be testable?"],
                "confirmation_criteria_defined": ["What confirmation criteria should be configured?", "What confirmation scenarios should exist?", "What confirmation states should be testable?"],
                "ensurance_criteria_defined": ["What ensurance criteria should be configured?", "What guarantee scenarios should exist?", "What assurance states should be testable?"],
                "assertion_criteria_defined": ["What assertion criteria should be configured?", "What assertion scenarios should exist?", "What assertion states should be testable?"],
                "test_criteria_defined": ["What test criteria should be configured?", "What testing scenarios should exist?", "What test states should be prepared?"],
                "examination_criteria_defined": ["What examination criteria should be configured?", "What inspection scenarios should exist?", "What examination states should be prepared?"],
                "inspection_criteria_defined": ["What inspection criteria should be configured?", "What review scenarios should exist?", "What inspection states should be prepared?"],
                "audit_criteria_defined": ["What audit criteria should be configured?", "What audit scenarios should exist?", "What audit states should be prepared?"],
                "upload_permissions": ["What upload permissions should be configured?", "What file upload scenarios should be available?", "What upload authorization states should exist?"],
                "download_permissions": ["What download permissions should be configured?", "What file download scenarios should be available?", "What download authorization states should exist?"],
                "export_permissions": ["What export permissions should be configured?", "What data export scenarios should be available?", "What export authorization states should exist?"],
                "import_permissions": ["What import permissions should be configured?", "What data import scenarios should be available?", "What import authorization states should exist?"],
                "attachment_permissions": ["What attachment permissions should be configured?", "What file attachment scenarios should be available?", "What attachment authorization states should exist?"],
                "sharing_permissions": ["What sharing permissions should be configured?", "What content sharing scenarios should be available?", "What sharing authorization states should exist?"],
                "transfer_permissions": ["What transfer permissions should be configured?", "What data transfer scenarios should be available?", "What transfer authorization states should exist?"],
                "copy_permissions": ["What copy permissions should be configured?", "What content copy scenarios should be available?", "What copy authorization states should exist?"],
                "move_permissions": ["What move permissions should be configured?", "What content move scenarios should be available?", "What move authorization states should exist?"],
                "rename_permissions": ["What rename permissions should be configured?", "What content rename scenarios should be available?", "What rename authorization states should exist?"],
                "communication_channel_available": ["What communication channels should be operational?", "What messaging states should exist?", "What communication scenarios should be testable?"],
                "email_service_configured": ["What email services should be configured?", "What email states should exist?", "What email scenarios should be testable?"],
                "notification_system_available": ["What notification systems should be operational?", "What notification states should exist?", "What notification scenarios should be testable?"],
                "alert_system_configured": ["What alert systems should be configured?", "What alert states should exist?", "What alert scenarios should be testable?"],
                "broadcast_permissions": ["What broadcast permissions should be configured?", "What message broadcast scenarios should be available?", "What broadcast authorization states should exist?"],
                "publishing_permissions": ["What publishing permissions should be configured?", "What content publishing scenarios should be available?", "What publishing authorization states should exist?"],
                "posting_permissions": ["What posting permissions should be configured?", "What content posting scenarios should be available?", "What posting authorization states should exist?"],
                "commenting_permissions": ["What commenting permissions should be configured?", "What comment scenarios should be available?", "What commenting authorization states should exist?"],
                "reply_permissions": ["What reply permissions should be configured?", "What reply scenarios should be available?", "What reply authorization states should exist?"],
                "admin_permissions": ["What admin permissions should be configured?", "What administrative scenarios should be available?", "What admin authorization states should exist?"],
                "setup_permissions": ["What setup permissions should be configured?", "What system setup scenarios should be available?", "What setup authorization states should exist?"],
                "init_permissions": ["What initialization permissions should be configured?", "What system init scenarios should be available?", "What init authorization states should exist?"],
                "customization_permissions": ["What customization permissions should be configured?", "What personalization scenarios should be available?", "What customization authorization states should exist?"],
                "personalization_permissions": ["What personalization permissions should be configured?", "What user preference scenarios should be available?", "What personalization authorization states should exist?"],
                "adjustment_permissions": ["What adjustment permissions should be configured?", "What settings modification scenarios should be available?", "What adjustment authorization states should exist?"],
                "tuning_permissions": ["What tuning permissions should be configured?", "What parameter adjustment scenarios should be available?", "What tuning authorization states should exist?"],
                "optimization_permissions": ["What optimization permissions should be configured?", "What performance tuning scenarios should be available?", "What optimization authorization states should exist?"],
                "monitoring_permissions": ["What monitoring permissions should be configured?", "What system monitoring scenarios should be available?", "What monitoring authorization states should exist?"],
                "tracking_permissions": ["What tracking permissions should be configured?", "What activity tracking scenarios should be available?", "What tracking authorization states should exist?"],
                "observation_permissions": ["What observation permissions should be configured?", "What event monitoring scenarios should be available?", "What observation authorization states should exist?"],
                "watching_permissions": ["What watching permissions should be configured?", "What content watching scenarios should be available?", "What watching authorization states should exist?"],
                "following_permissions": ["What following permissions should be configured?", "What user/entity following scenarios should be available?", "What following authorization states should exist?"],
                "logging_permissions": ["What logging permissions should be configured?", "What log access scenarios should be available?", "What logging authorization states should exist?"],
                "audit_permissions": ["What audit permissions should be configured?", "What audit access scenarios should be available?", "What audit authorization states should exist?"],
                "tracing_permissions": ["What tracing permissions should be configured?", "What operation tracing scenarios should be available?", "What tracing authorization states should exist?"],
                "approval_permissions": ["What approval permissions should be configured?", "What item approval scenarios should be available?", "What approval authorization states should exist?"],
                "approval_workflow_active": ["What approval workflows should be active?", "What approval process states should exist?", "What approval scenarios should be testable?"],
                "rejection_permissions": ["What rejection permissions should be configured?", "What item rejection scenarios should be available?", "What rejection authorization states should exist?"],
                "rejection_workflow_active": ["What rejection workflows should be active?", "What rejection process states should exist?", "What rejection scenarios should be testable?"],
                "review_permissions": ["What review permissions should be configured?", "What item review scenarios should be available?", "What review authorization states should exist?"],
                "assignment_permissions": ["What assignment permissions should be configured?", "What task assignment scenarios should be available?", "What assignment authorization states should exist?"],
                "assignee_exists": ["What assignee roles should be available?", "What assignment target scenarios should exist?", "What assignee states should be prepared?"],
                "delegation_permissions": ["What delegation permissions should be configured?", "What task delegation scenarios should be available?", "What delegation authorization states should exist?"],
                "delegate_exists": ["What delegate roles should be available?", "What delegation target scenarios should exist?", "What delegate states should be prepared?"],
                "escalation_permissions": ["What escalation permissions should be configured?", "What issue escalation scenarios should be available?", "What escalation authorization states should exist?"],
                "escalation_path_defined": ["What escalation paths should be defined?", "What escalation routing scenarios should exist?", "What escalation process states should be prepared?"],
                "resolution_permissions": ["What resolution permissions should be configured?", "What issue resolution scenarios should be available?", "What resolution authorization states should exist?"],
                "closure_permissions": ["What closure permissions should be configured?", "What item closure scenarios should be available?", "What closure authorization states should exist?"],
                "reopen_permissions": ["What reopen permissions should be configured?", "What item reopening scenarios should be available?", "What reopen authorization states should exist?"],
                "default": ["What system state or user context is required?", "What preconditions must be met?", "What state conditions should exist?"]
            }
        }

    def generate_suggestions(self, issues: List[Union[AmbiguityIssue, AssumptionIssue]],
                           text: str, always_ask: bool = True) -> List[str]:
        """
        Generate clarifying questions for ALL test cases, not just problematic ones.

        Args:
            issues: Detected issues (may be empty)
            text: Original test case text
            always_ask: Whether to always provide questions (default: True)

        Returns:
            List of clarifying question strings
        """
        suggestions = []

        # Always include standard clarifying questions for test cases
        if always_ask:
            suggestions.extend(self._get_standard_test_case_questions(text))

        # Add issue-specific questions if any issues detected
        for issue in issues:
            if isinstance(issue, AmbiguityIssue):
                suggestion = self._generate_ambiguity_suggestion(issue)
            elif isinstance(issue, AssumptionIssue):
                suggestion = self._generate_assumption_suggestion(issue)
            else:
                continue

            if suggestion and suggestion not in suggestions:  # Avoid duplicates
                suggestions.append(suggestion)

        return suggestions

    def _get_standard_test_case_questions(self, text: str) -> List[str]:
        """
        Standard clarifying questions that should be asked for EVERY test case.
        These ensure comprehensive test case quality regardless of detected issues.
        """
        standard_questions = [
            "What are the exact preconditions required for this test?",
            "What is the expected result and how should it be verified?",
            "What test data or test accounts are needed?",
            "Are there any timing or synchronization requirements?",
            "What should happen if the test fails - any cleanup needed?",
            "Does this test have any dependencies on other tests?",
            "What are the acceptable performance thresholds?",
            "How should edge cases or error conditions be handled?",
            "What logging or reporting is required during test execution?",
            "Are there any environment-specific considerations?"
        ]

        # Add context-specific questions based on text analysis
        if self._contains_action_words(text):
            standard_questions.append("What are the specific user actions and their sequence?")

        if self._contains_data_operations(text):
            standard_questions.append("What data states should exist before and after the test?")

        if self._contains_ui_interactions(text):
            standard_questions.append("What are the exact UI element selectors and interaction methods?")

        return standard_questions[:8]  # Return top 8 to avoid overwhelming

    def _contains_action_words(self, text: str) -> bool:
        """Check if text contains action words."""
        action_words = ['click', 'tap', 'press', 'select', 'type', 'enter', 'submit', 'save']
        return any(word in text.lower() for word in action_words)

    def _contains_data_operations(self, text: str) -> bool:
        """Check if text contains data operations."""
        data_words = ['create', 'update', 'delete', 'add', 'edit', 'modify', 'remove']
        return any(word in text.lower() for word in data_words)

    def _contains_ui_interactions(self, text: str) -> bool:
        """Check if text contains UI interactions."""
        ui_words = ['button', 'field', 'form', 'page', 'screen', 'menu', 'dialog']
        return any(word in text.lower() for word in ui_words)

    def _generate_ambiguity_suggestion(self, issue: AmbiguityIssue) -> str:
        """Generate suggestion for ambiguity issue."""
        issue_type = issue.type
        issue_text = issue.text.lower()

        if issue_type in self.ambiguity_suggestions:
            templates = self.ambiguity_suggestions[issue_type]

            # Try exact match first
            if issue_text in templates:
                template_list = templates[issue_text]
                if isinstance(template_list, list):
                    return template_list[0]  # Return first suggestion
                else:
                    return template_list

            # Try default for the type
            if "default" in templates:
                default_templates = templates["default"]
                if isinstance(default_templates, list):
                    return default_templates[0]  # Return first suggestion
                else:
                    return default_templates

        # Fallback suggestion
        return f"What specific criteria define '{issue.text}'?"

    def _generate_assumption_suggestion(self, issue: AssumptionIssue) -> str:
        """Generate suggestion for assumption issue."""
        category = issue.category

        if category in self.assumption_suggestions:
            templates = self.assumption_suggestions[category]

            # Try to match based on assumption text or type
            assumption_key = self._extract_assumption_key(issue)
            if assumption_key in templates:
                template_list = templates[assumption_key]
                if isinstance(template_list, list):
                    return template_list[0]  # Return first suggestion
                else:
                    return template_list

            # Try text-based matching
            issue_text_lower = issue.text.lower()
            for key, template in templates.items():
                if key != "default" and key in issue_text_lower:
                    if isinstance(template, list):
                        return template[0]  # Return first suggestion
                    else:
                        return template

            # Try default for the category
            if "default" in templates:
                default_templates = templates["default"]
                if isinstance(default_templates, list):
                    return default_templates[0]  # Return first suggestion
                else:
                    return default_templates

        # Fallback suggestion
        return f"What specific {category.lower()} requirements are needed?"

    def _extract_assumption_key(self, issue: AssumptionIssue) -> str:
        """Extract a key from assumption issue for template matching."""
        # Try to extract key from assumption text
        assumption_lower = issue.assumption.lower()

        key_mappings = {
            "user exists": "user_exists",
            "credentials": "credentials_exist",
            "logged in": "user_logged_in",
            "permissions": "permissions_granted",
            "form filled": "form_filled",
            "data entered": "data_entered",
            "record exists": "record_exists",
            "condition exists": "condition_exists",
            "data exists": "data_exists",
            "error": "error_trigger",
            "failure": "failure_condition",
            "admin": "admin_role",
            "manager": "manager_role",
            "user": "user_role",
            "file exists": "file_exists",
            "recipient exists": "recipient_exists",
            "sender exists": "sender_exists",
            "task exists": "task_exists",
            "item exists": "item_exists",
            "issue exists": "issue_exists",
            "page exists": "page_exists",
            "resource exists": "resource_exists",
            "content exists": "content_exists",
            "space available": "space_available",
            "container exists": "container_exists",
            "position valid": "position_valid",
            "list exists": "list_exists",
            "search index exists": "search_index_exists",
            "sortable data exists": "sortable_data_exists",
            "searchable content exists": "searchable_content_exists",
            "query engine available": "query_engine_available",
            "searchable items exist": "searchable_items_exist",
            "lookup table exists": "lookup_table_exists",
            "data source available": "data_source_available",
            "api endpoint available": "api_endpoint_available",
            "resource accessible": "resource_accessible",
            "verification criteria defined": "verification_criteria_defined",
            "check criteria defined": "check_criteria_defined",
            "validation rules defined": "validation_rules_defined",
            "confirmation criteria defined": "confirmation_criteria_defined",
            "ensurance criteria defined": "ensurance_criteria_defined",
            "assertion criteria defined": "assertion_criteria_defined",
            "test criteria defined": "test_criteria_defined",
            "examination criteria defined": "examination_criteria_defined",
            "inspection criteria defined": "inspection_criteria_defined",
            "audit criteria defined": "audit_criteria_defined",
            "upload permissions": "upload_permissions",
            "download permissions": "download_permissions",
            "export permissions": "export_permissions",
            "import permissions": "import_permissions",
            "attachment permissions": "attachment_permissions",
            "sharing permissions": "sharing_permissions",
            "transfer permissions": "transfer_permissions",
            "copy permissions": "copy_permissions",
            "move permissions": "move_permissions",
            "rename permissions": "rename_permissions",
            "communication channel available": "communication_channel_available",
            "email service configured": "email_service_configured",
            "notification system available": "notification_system_available",
            "alert system configured": "alert_system_configured",
            "broadcast permissions": "broadcast_permissions",
            "publishing permissions": "publishing_permissions",
            "posting permissions": "posting_permissions",
            "commenting permissions": "commenting_permissions",
            "reply permissions": "reply_permissions",
            "admin permissions": "admin_permissions",
            "setup permissions": "setup_permissions",
            "init permissions": "init_permissions",
            "customization permissions": "customization_permissions",
            "personalization permissions": "personalization_permissions",
            "adjustment permissions": "adjustment_permissions",
            "tuning permissions": "tuning_permissions",
            "optimization permissions": "optimization_permissions",
            "monitoring permissions": "monitoring_permissions",
            "tracking permissions": "tracking_permissions",
            "observation permissions": "observation_permissions",
            "watching permissions": "watching_permissions",
            "following permissions": "following_permissions",
            "logging permissions": "logging_permissions",
            "audit permissions": "audit_permissions",
            "tracing permissions": "tracing_permissions",
            "approval permissions": "approval_permissions",
            "approval workflow active": "approval_workflow_active",
            "rejection permissions": "rejection_permissions",
            "rejection workflow active": "rejection_workflow_active",
            "review permissions": "review_permissions",
            "assignment permissions": "assignment_permissions",
            "assignee exists": "assignee_exists",
            "delegation permissions": "delegation_permissions",
            "delegate exists": "delegate_exists",
            "escalation permissions": "escalation_permissions",
            "escalation path defined": "escalation_path_defined",
            "resolution permissions": "resolution_permissions",
            "closure permissions": "closure_permissions",
            "reopen permissions": "reopen_permissions",
            "account active": "account_active",
            "form valid": "form_valid"
        }

        for phrase, key in key_mappings.items():
            if phrase in assumption_lower:
                return key

        return "default"

    def generate_issue_specific_suggestions(self, issues: List[Union[AmbiguityIssue, AssumptionIssue]]) -> Dict[str, List[str]]:
        """
        Generate suggestions grouped by issue type for detailed reporting.

        Args:
            issues: List of detected issues

        Returns:
            Dictionary mapping issue types to lists of suggestions
        """
        grouped_suggestions = {
            "ambiguity": [],
            "assumptions": []
        }

        for issue in issues:
            if isinstance(issue, AmbiguityIssue):
                suggestion = self._generate_ambiguity_suggestion(issue)
                if suggestion not in grouped_suggestions["ambiguity"]:
                    grouped_suggestions["ambiguity"].append(suggestion)
            elif isinstance(issue, AssumptionIssue):
                suggestion = self._generate_assumption_suggestion(issue)
                if suggestion not in grouped_suggestions["assumptions"]:
                    grouped_suggestions["assumptions"].append(suggestion)

        return grouped_suggestions