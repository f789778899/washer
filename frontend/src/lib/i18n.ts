export type Language = "zh" | "en";

export const copy = {
  zh: {
    menu: {
      language: "语言",
      chinese: "中文",
      english: "English",
      theme: "主题",
      light: "白天",
      dark: "夜间",
      tutorial: "教程",
      export: "导出",
      exportJob: "导出当前任务",
      exportDoc: "导出当前文档",
      close: "关闭"
    },
    app: {
      eyebrow: "企业 RAG 数据流入",
      title: "DocFlow Studio",
      subtitle: "在文档进入知识库前，自动完成解析、去重、清洗、脱敏与结构化输出。",
      status: "实时状态",
      ready: "系统就绪。",
      refresh: "最后刷新",
      uploadCreated: "上传任务已创建",
      pathCreated: "路径任务已创建",
      exported: "导出完成"
    },
    metrics: {
      documents: "文档数",
      documentsHelp: "已处理并索引的结果",
      duplicates: "重复",
      duplicatesHelp: "精确或近似重复",
      redacted: "脱敏",
      redactedHelp: "包含敏感字段处理的文档",
      avgQuality: "平均质量",
      high: "输出质量高，可直接进入下游",
      good: "质量良好，建议抽检",
      review: "建议复核数据质量"
    },
    upload: {
      title: "导入控制台",
      description: "上传文件，或提交本机文件/文件夹路径进行批量预处理。",
      tenant: "租户 ID",
      fileUpload: "文件上传",
      accepts: "支持 PDF、DOCX、TXT、Markdown、邮件、日志和 HTML 导出。",
      noFiles: "未选择文件",
      createUpload: "创建上传任务",
      pathIntake: "路径导入",
      pathHelp: "每行填写一个绝对文件或文件夹路径，桌面批处理时很方便。",
      createPath: "创建路径任务",
      submitting: "提交中..."
    },
    jobs: {
      title: "任务",
      description: "查看导入任务的状态、吞吐和失败情况。",
      id: "任务 ID",
      status: "状态",
      tenant: "租户",
      sources: "源文件",
      processed: "已处理",
      failed: "失败",
      updated: "更新时间"
    },
    docs: {
      title: "处理结果",
      description: "选择文档后查看脱敏 Markdown、元数据和审计记录。",
      empty: "请选择一个任务来加载处理结果。",
      noRedaction: "无脱敏字段",
      quality: "质量",
      viewer: "结果查看器",
      viewerHelp: "结构化输出、元数据和安全审计集中展示。",
      noSelection: "请选择一个已处理文档查看结果。",
      markdown: "脱敏 Markdown",
      metadata: "Metadata",
      cleaning: "清洗动作",
      dedup: "去重关系",
      sensitive: "脱敏命中"
    },
    export: {
      title: "导出 / 另存为",
      target: "目标文件夹",
      format: "输出格式",
      scope: "导出范围",
      job: "当前任务全部文档",
      document: "当前文档",
      submit: "开始导出",
      cancel: "取消",
      hint: "填写本机绝对路径，程序会为每个文档单独生成文件。",
      noTarget: "请先填写导出目录。",
      noJob: "请先选择任务。",
      noDocument: "请先选择文档。"
    },
    tutorial: {
      title: "手动使用教程",
      steps: [
        "1. 在“导入控制台”里确认租户 ID。单机测试可以使用 demo-tenant，企业环境建议按部门或客户设置。",
        "2. 选择“文件上传”可一次上传多个文件；选择“路径导入”可填写一个或多个本机文件夹路径。",
        "3. 创建任务后，程序会在后台自动解析、清洗、去重、脱敏并生成结构化 Markdown。",
        "4. 在“任务”表格中点击任意任务，下方“处理结果”会立刻切换到该任务的文档列表。",
        "5. 点击某个文档卡片，右侧会显示脱敏后的 Markdown、metadata、清洗动作、去重关系和脱敏审计。",
        "6. 需要给 RAG 管线使用时，点击顶部“导出”，选择当前任务或当前文档，填写目标文件夹并选择 md 或 txt。",
        "7. 导出的文件名会保留原文件名并追加 document_id，避免同名覆盖。"
      ]
    }
  },
  en: {
    menu: {
      language: "Language",
      chinese: "中文",
      english: "English",
      theme: "Theme",
      light: "Light",
      dark: "Dark",
      tutorial: "Guide",
      export: "Export",
      exportJob: "Export Job",
      exportDoc: "Export Document",
      close: "Close"
    },
    app: {
      eyebrow: "Enterprise RAG Intake",
      title: "DocFlow Studio",
      subtitle:
        "Parse, deduplicate, clean, redact, and structure documents before knowledge-base ingestion.",
      status: "Live status",
      ready: "System ready.",
      refresh: "Last refresh",
      uploadCreated: "Upload job created",
      pathCreated: "Path job created",
      exported: "Export completed"
    },
    metrics: {
      documents: "Documents",
      documentsHelp: "Processed artifacts indexed",
      duplicates: "Duplicates",
      duplicatesHelp: "Exact or near duplicate detections",
      redacted: "Redacted",
      redactedHelp: "Documents with sensitive fields masked",
      avgQuality: "Avg Quality",
      high: "High confidence output quality",
      good: "Good quality with some review recommended",
      review: "Needs stronger data hygiene review"
    },
    upload: {
      title: "Ingestion Control",
      description: "Upload files or submit local file and folder paths for batch preprocessing.",
      tenant: "Tenant ID",
      fileUpload: "File Upload",
      accepts: "Accepts PDF, DOCX, TXT, Markdown, email, log, and HTML exports.",
      noFiles: "No files selected",
      createUpload: "Create Upload Job",
      pathIntake: "Path Intake",
      pathHelp: "One absolute file or directory path per line. Useful for desktop batch runs.",
      createPath: "Create Path Job",
      submitting: "Submitting..."
    },
    jobs: {
      title: "Jobs",
      description: "Monitor status, throughput, and partial failures across ingestion runs.",
      id: "Job ID",
      status: "Status",
      tenant: "Tenant",
      sources: "Sources",
      processed: "Processed",
      failed: "Failed",
      updated: "Updated"
    },
    docs: {
      title: "Processed Documents",
      description: "Select a document to inspect redacted Markdown, metadata, and audit events.",
      empty: "Choose a job to load processed documents.",
      noRedaction: "No redaction",
      quality: "Q",
      viewer: "Result Viewer",
      viewerHelp: "Structured output, metadata, and security audit details stay together.",
      noSelection: "Select a processed document to view its structured output.",
      markdown: "Redacted Markdown",
      metadata: "Metadata",
      cleaning: "Cleaning Actions",
      dedup: "Dedup Relations",
      sensitive: "Sensitive Matches"
    },
    export: {
      title: "Export / Save As",
      target: "Target Folder",
      format: "Output Format",
      scope: "Export Scope",
      job: "All documents in current job",
      document: "Current document",
      submit: "Export",
      cancel: "Cancel",
      hint: "Enter a local absolute path. Each document will be written as a separate file.",
      noTarget: "Please enter a target folder.",
      noJob: "Please select a job first.",
      noDocument: "Please select a document first."
    },
    tutorial: {
      title: "Manual Guide",
      steps: [
        "1. Confirm the tenant ID in Ingestion Control. Use demo-tenant for local tests.",
        "2. Use File Upload for multiple files, or Path Intake for local folders.",
        "3. After job creation, DocFlow parses, cleans, deduplicates, redacts, and formats results.",
        "4. Click any job row to switch the processed document list immediately.",
        "5. Click a document card to inspect Markdown, metadata, cleaning, dedup, and redaction audit.",
        "6. Use the top Export menu to save the current job or document as md or txt.",
        "7. Exported filenames include the original name and document_id to prevent overwrite."
      ]
    }
  }
} as const;
