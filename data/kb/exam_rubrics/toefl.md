# TOEFL iBT Writing 官方评分指南（ETS Official Scoring Guide）

来源：ETS官方公开PDF（ets.org/toefl），版权归ETS所有。TOEFL iBT改版后Writing
部分包含两类任务：Integrated Writing（综合写作，需要先读一篇文章、再听一段
讲座，写作内容围绕两者的关系展开）和两个独立写作任务——Write an Email（写
邮件）、Writing for an Academic Discussion（学术讨论区回帖）。**本系统只支持
后两个独立写作任务**（对应`src/exam_types.py`的`TOEFL_SUBTYPES`），因为
Integrated Writing需要完整的阅读材料+讲座音频作为刺激材料，一篇孤立提交的
纯文本作文没有对应的阅读/听力素材可供评分参照。下面同时收录了Integrated
Writing的官方评分指南作为参考（本系统实际不用它评分，只是完整收录官方素材
方便查阅），Email/Academic Discussion两套指南是本系统真正在用的评分依据。

三套指南都按0-5整数评分。

## Write an Email 评分指南（本系统TOEFL子类型选"Write an Email"时使用）

### Score 5 — A fully successful response
The response is effective, is clearly expressed, and shows consistent facility in the use of language.
A typical response displays the following:
- Elaboration that effectively supports the communicative purpose
- Effective syntactic variety and precise, idiomatic word choice
- Consistent use of appropriate social conventions (e.g., politeness, register, organization of information and formulation of actions such as requests, refusals, criticisms, etc.)
- Almost no lexical or grammatical errors other than those expected from a competent writer writing under timed conditions (e.g., common typos or common misspellings or substitutions like there/their)

### Score 4 — A generally successful response
The response is mostly effective and easily understood. Language facility is adequate to the task.
A typical response displays the following:
- Adequate elaboration to support the communicative purpose
- Syntactic variety and appropriate word choice
- Mostly appropriate social conventions
- Few lexical or grammatical errors

### Score 3 — A partially successful response
The response generally accomplishes the task. Limitations in language facility may prevent parts of the message from being fully clear and effective.
A typical response displays the following:
- Elaboration that partially supports the communicative purpose
- A moderate range of syntax and vocabulary
- Some noticeable errors in structure, word forms, use of idiomatic language and/or social conventions

### Score 2 — A mostly unsuccessful response
The response reflects an attempt to address the task, but it is mostly ineffective. The message may be limited or difficult to interpret.
A typical response exhibits one or more of the following:
- Limited or irrelevant elaboration
- Some connected sentence-level language, with a limited range of syntax and vocabulary
- An accumulation of errors in sentence structure and/or language use

### Score 1 — An unsuccessful response
The response reflects an ineffective attempt to address the task. The message may be limited to the point of being unintelligible.
A typical response exhibits one or more of the following:
- Very little elaboration, if any
- Telegraphic language (i.e., short and/or disconnected phrases and sentences) with a very limited range of vocabulary
- Serious and frequent errors in the use of language
- Minimal original language; any coherent language is mostly borrowed from the stimulus

### Score 0
The response is blank, rejects the topic, is not in English, is entirely copied from the prompt, is entirely unconnected to the prompt or consists of arbitrary keystrokes.

## Writing for an Academic Discussion 评分指南

### Score 5 — A fully successful response
The response is a relevant and very clearly expressed contribution to the online discussion, and it demonstrates consistent facility in the use of language.
A typical response displays the following:
- Relevant and well-elaborated explanations, exemplifications, and/or details
- Effective use of a variety of syntactic structures and precise, idiomatic word choice
- Almost no lexical or grammatical errors other than those expected from a competent writer writing under timed conditions (e.g., common typos or common misspellings or substitutions like there/their)

### Score 4 — A generally successful response
The response is a relevant contribution to the online discussion, and facility in the use of language allows the writer's ideas to be easily understood.
A typical response displays the following:
- Relevant and adequately elaborated explanations, exemplifications, and/or details
- A variety of syntactic structures and appropriate word choice
- Few lexical or grammatical errors

### Score 3 — A partially successful response
The response is a mostly relevant and mostly understandable contribution to the online discussion, and there is some facility in the use of language.
A typical response displays the following:
- Elaboration in which part of an explanation, example, or detail may be missing, unclear, or irrelevant
- Some variety in syntactic structures and a range of vocabulary
- Some noticeable lexical and grammatical errors in sentence structure, word form, or use of idiomatic language

### Score 2 — A mostly unsuccessful response
The response reflects an attempt to contribute to the online discussion, but limitations in the use of language may make ideas hard to follow.
A typical response displays the following:
- Ideas that may be poorly elaborated or only partially relevant
- A limited range of syntactic structures and vocabulary
- An accumulation of errors in sentence structure, word forms, or use

### Score 1 — An unsuccessful response
The response reflects an ineffective attempt to contribute to the online discussion, and limitations in the use of language may prevent the expression of ideas.
A typical response displays the following:
- Words and phrases that indicate an attempt to address the task but with few or no coherent ideas
- Severely limited range of syntactic structures and vocabulary
- Serious and frequent errors in the use of language
- Minimal original language; any coherent language is mostly borrowed from the stimulus

### Score 0
The response is blank, rejects the topic, is not in English, is entirely copied from the prompt, is entirely unconnected to the prompt, or consists of arbitrary keystrokes.

## Integrated Writing Rubric（官方参考，本系统不用它评分）

### Score 5
A response at this level successfully selects the important information from the lecture and coherently and accurately presents this information in relation to the relevant information presented in the reading. The response is well organized, and occasional language errors that are present do not result in inaccurate or imprecise presentation of content or connections.

### Score 4
A response at this level is generally good in selecting the important information from the lecture and in coherently and accurately presenting this information in relation to the relevant information in the reading, but it may have minor omission, inaccuracy, vagueness, or imprecision of some content from the lecture or in connection to points made in the reading. A response is also scored at this level if it has more frequent or noticeable minor language errors, as long as such usage and grammatical structures do not result in anything more than an occasional lapse of clarity or in the connection of ideas.

### Score 3
A response at this level contains some important information from the lecture and conveys some relevant connection to the reading, but it is marked by one or more of: only vague/global/unclear connection of lecture points to reading points; omission of one major key point from the lecture; incomplete/inaccurate/imprecise key points or connections; more frequent errors of usage/grammar causing noticeably vague expressions or obscured meanings.

### Score 2
A response at this level contains some relevant information from the lecture, but is marked by significant language difficulties or by significant omission or inaccuracy of important ideas from the lecture or in the connections between the lecture and the reading.

### Score 1
A response at this level provides little or no meaningful or relevant coherent content from the lecture, and/or the language level is so low that it is difficult to derive meaning.

### Score 0
A response at this level merely copies sentences from the reading, rejects the topic or is otherwise not connected to the topic, is written in a foreign language, consists of keystroke characters, or is blank.

## 本系统评分映射

`src/official_rubrics.py`的`TOEFL`量表要求LLM输出单一键`task_score`（0-5
整数），根据题目实际类型（Email/Academic Discussion）适用上面对应那一套
评分标准原文来判断分数，不使用Integrated Writing那套（本系统不支持这个
任务类型）。系统不把这个单题分换算成完整TOEFL Writing section的1-6分或
0-30量表分，因为正式Writing部分是Email+Academic Discussion两题的综合结果，
本系统一次只评一篇。
