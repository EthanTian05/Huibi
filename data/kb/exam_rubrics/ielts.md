# IELTS Writing 官方评分标准（Band Descriptors，公开版本）

来源：IELTS官方公开版 Writing Band Descriptors（IELTS由British Council、
IDP: IELTS Australia、Cambridge English Language Assessment共同所有）。下面
Task 1为学术类（Academic）版本。本系统对应`src/official_rubrics.py`里的
`IELTS`（Task 2）和`IELTS_TASK1`两套量表，键名映射见文末"本系统评分映射"。

## Writing Task 2（议论文）Band Descriptors

Task 2按四个标准各给0-9整数Band：Task Response（任务回应）、Coherence and
Cohesion（连贯与衔接）、Lexical Resource（词汇资源）、Grammatical Range and
Accuracy（语法多样性与准确性），四项等权平均后四舍五入到最近0.5得到该篇总分。

### Band 9
- Task Response：fully addresses all parts of the task; presents a fully developed position in answer to the question with relevant, fully extended and well supported ideas.
- Coherence and Cohesion：uses cohesion in such a way that it attracts no attention; skilfully manages paragraphing.
- Lexical Resource：uses a wide range of vocabulary with very natural and sophisticated control of lexical features; rare minor errors occur only as 'slips'.
- Grammatical Range and Accuracy：uses a wide range of structures with full flexibility and accuracy; rare minor errors occur only as 'slips'.

### Band 8
- Task Response：sufficiently addresses all parts of the task; presents a well-developed response to the question with relevant, extended and supported ideas.
- Coherence and Cohesion：sequences information and ideas logically; manages all aspects of cohesion well; uses paragraphing sufficiently and appropriately.
- Lexical Resource：uses a wide range of vocabulary fluently and flexibly to convey precise meanings; skilfully uses uncommon lexical items but there may be occasional inaccuracies in word choice and collocation; produces rare errors in spelling and/or word formation.
- Grammatical Range and Accuracy：uses a wide range of structures; the majority of sentences are error-free; makes only very occasional errors or inappropriacies.

### Band 7
- Task Response：addresses all parts of the task; presents a clear position throughout the response; presents, extends and supports main ideas, but there may be a tendency to over-generalise and/or supporting ideas may lack focus.
- Coherence and Cohesion：logically organises information and ideas; there is clear progression throughout; uses a range of cohesive devices appropriately although there may be some under-/over-use; presents a clear central topic within each paragraph.
- Lexical Resource：uses a sufficient range of vocabulary to allow some flexibility and precision; uses less common lexical items with some awareness of style and collocation; may produce occasional errors in word choice, spelling and/or word formation.
- Grammatical Range and Accuracy：uses a variety of complex structures; produces frequent error-free sentences; has good control of grammar and punctuation but may make a few errors.

### Band 6
- Task Response：addresses all parts of the task although some parts may be more fully covered than others; presents a relevant position although the conclusions may become unclear or repetitive; presents relevant main ideas but some may be inadequately developed/unclear.
- Coherence and Cohesion：arranges information and ideas coherently and there is a clear overall progression; uses cohesive devices effectively, but cohesion within and/or between sentences may be faulty or mechanical; may not always use referencing clearly or appropriately; uses paragraphing, but not always logically.
- Lexical Resource：uses an adequate range of vocabulary for the task; attempts to use less common vocabulary but with some inaccuracy; makes some errors in spelling and/or word formation, but they do not impede communication.
- Grammatical Range and Accuracy：uses a mix of simple and complex sentence forms; makes some errors in grammar and punctuation but they rarely reduce communication.

### Band 5
- Task Response：addresses the task only partially; the format may be inappropriate in places; expresses a position but the development is not always clear and there may be no conclusions drawn; presents some main ideas but these are limited and not sufficiently developed; there may be irrelevant detail.
- Coherence and Cohesion：presents information with some organisation but there may be a lack of overall progression; makes inadequate, inaccurate or over-use of cohesive devices; may be repetitive because of lack of referencing and substitution; may not write in paragraphs, or paragraphing may be inadequate.
- Lexical Resource：uses a limited range of vocabulary, but this is minimally adequate for the task; may make noticeable errors in spelling and/or word formation that may cause some difficulty for the reader.
- Grammatical Range and Accuracy：uses only a limited range of structures; attempts complex sentences but these tend to be less accurate than simple sentences; may make frequent grammatical errors and punctuation may be faulty; errors can cause some difficulty for the reader.

### Band 4
- Task Response：responds to the task only in a minimal way or the answer is tangential; the format may be inappropriate; presents a position but this is unclear; presents some main ideas but these are difficult to identify and may be repetitive, irrelevant or not well supported.
- Coherence and Cohesion：presents information and ideas but these are not arranged coherently and there is no clear progression in the response; uses some basic cohesive devices but these may be inaccurate or repetitive; may not write in paragraphs or their use may be confusing.
- Lexical Resource：uses only basic vocabulary which may be used repetitively or which may be inappropriate for the task; has limited control of word formation and/or spelling; errors may cause strain for the reader.
- Grammatical Range and Accuracy：uses only a very limited range of structures with only rare use of subordinate clauses; some structures are accurate but errors predominate, and punctuation is often faulty.

### Band 3
- Task Response：does not adequately address any part of the task; does not express a clear position; presents few ideas, which are largely undeveloped or irrelevant.
- Coherence and Cohesion：does not organise ideas logically; may use a very limited range of cohesive devices, and those used may not indicate a logical relationship between ideas.
- Lexical Resource：uses only a very limited range of words and expressions with very limited control of word formation and/or spelling; errors may severely distort the message.
- Grammatical Range and Accuracy：attempts sentence forms but errors in grammar and punctuation predominate and distort the meaning.

### Band 2
- Task Response：barely responds to the task; does not express a position; may attempt to present one or two ideas but there is no development.
- Coherence and Cohesion：has very little control of organisational features.
- Lexical Resource：uses an extremely limited range of vocabulary; essentially no control of word formation and/or spelling.
- Grammatical Range and Accuracy：cannot use sentence forms except in memorised phrases.

### Band 1
- Task Response：answer is completely unrelated to the task.
- Coherence and Cohesion：fails to communicate any message.
- Lexical Resource：can only use a few isolated words.
- Grammatical Range and Accuracy：cannot use sentence forms at all.

### Band 0
does not attend / does not attempt the task in any way / writes a totally memorised response（所有四项）。

## Writing Task 1（学术类：图表/表格/流程图/地图描述）Band Descriptors

Task 1的第一项标准换成Task Achievement（任务完成情况），替代Task 2的Task
Response；其余三项（Coherence and Cohesion、Lexical Resource、Grammatical
Range and Accuracy）标准与Task 2相同结构，但描述针对图表描述任务改写。计分
方式同样是四项等权平均后四舍五入到最近0.5。

### Band 9
- Task Achievement：fully satisfies all the requirements of the task; clearly presents a fully developed response.
- Coherence and Cohesion：uses cohesion in such a way that it attracts no attention; skilfully manages paragraphing.
- Lexical Resource：uses a wide range of vocabulary with very natural and sophisticated control of lexical features; rare minor errors occur only as 'slips'.
- Grammatical Range and Accuracy：uses a wide range of structures with full flexibility and accuracy; rare minor errors occur only as 'slips'.

### Band 8
- Task Achievement：covers all requirements of the task sufficiently; presents, highlights and illustrates key features/bullet points clearly and appropriately.
- Coherence and Cohesion：sequences information and ideas logically; manages all aspects of cohesion well; uses paragraphing sufficiently and appropriately.
- Lexical Resource：uses a wide range of vocabulary fluently and flexibly to convey precise meanings; skilfully uses uncommon lexical items but there may be occasional inaccuracies in word choice and collocation; produces rare errors in spelling and/or word formation.
- Grammatical Range and Accuracy：uses a wide range of structures; the majority of sentences are error-free; makes only very occasional errors or inappropriacies.

### Band 7
- Task Achievement：covers the requirements of the task; presents a clear overview of main trends, differences or stages; clearly presents and highlights key features/bullet points but could be more fully extended.
- Coherence and Cohesion：logically organises information and ideas; there is clear progression throughout; uses a range of cohesive devices appropriately although there may be some under-/over-use.
- Lexical Resource：uses a sufficient range of vocabulary to allow some flexibility and precision; uses less common lexical items with some awareness of style and collocation; may produce occasional errors in word choice, spelling and/or word formation.
- Grammatical Range and Accuracy：uses a variety of complex structures; produces frequent error-free sentences; has good control of grammar and punctuation but may make a few errors.

### Band 6
- Task Achievement：addresses the requirements of the task; presents an overview with information appropriately selected; presents and adequately highlights key features/bullet points but details may be irrelevant, inappropriate or inaccurate.
- Coherence and Cohesion：arranges information and ideas coherently and there is a clear overall progression; uses cohesive devices effectively, but cohesion within and/or between sentences may be faulty or mechanical; may not always use referencing clearly or appropriately.
- Lexical Resource：uses an adequate range of vocabulary for the task; attempts to use less common vocabulary but with some inaccuracy; makes some errors in spelling and/or word formation, but they do not impede communication.
- Grammatical Range and Accuracy：uses a mix of simple and complex sentence forms; makes some errors in grammar and punctuation but they rarely reduce communication.

### Band 5
- Task Achievement：generally addresses the task; the format may be inappropriate in places; recounts detail mechanically with no clear overview; there may be no data to support the description.
- Coherence and Cohesion：presents information with some organisation but there may be a lack of overall progression; makes inadequate, inaccurate or over-use of cohesive devices; may be repetitive because of lack of referencing and substitution.
- Lexical Resource：uses a limited range of vocabulary, but this is minimally adequate for the task; may make noticeable errors in spelling and/or word formation that may cause some difficulty for the reader.
- Grammatical Range and Accuracy：uses only a limited range of structures; attempts complex sentences but these tend to be less accurate than simple sentences; may make frequent grammatical errors and punctuation may be faulty; errors can cause some difficulty for the reader.

### Band 4
- Task Achievement：attempts to address the task but does not cover all key features/bullet points; the format may be inappropriate; may confuse key features/bullet points with detail; parts may be unclear, irrelevant, repetitive or inaccurate.
- Coherence and Cohesion：presents information and ideas but these are not arranged coherently and there is no clear progression in the response; uses some basic cohesive devices but these may be inaccurate or repetitive.
- Lexical Resource：uses only basic vocabulary which may be used repetitively or which may be inappropriate for the task; has limited control of word formation and/or spelling; errors may cause strain for the reader.
- Grammatical Range and Accuracy：uses only a very limited range of structures with only rare use of subordinate clauses; some structures are accurate but errors predominate, and punctuation is often faulty.

### Band 3
- Task Achievement：fails to address the task, which may have been completely misunderstood; presents limited ideas which may be largely irrelevant/repetitive.
- Coherence and Cohesion：does not organise ideas logically; may use a very limited range of cohesive devices, and those used may not indicate a logical relationship between ideas.
- Lexical Resource：uses only a very limited range of words and expressions with very limited control of word formation and/or spelling; errors may severely distort the message.
- Grammatical Range and Accuracy：attempts sentence forms but errors in grammar and punctuation predominate and distort the meaning.

### Band 2
- Task Achievement：answer is barely related to the task.
- Coherence and Cohesion：has very little control of organisational features.
- Lexical Resource：uses an extremely limited range of vocabulary; essentially no control of word formation and/or spelling.
- Grammatical Range and Accuracy：cannot use sentence forms except in memorised phrases.

### Band 1
- Task Achievement：answer is completely unrelated to the task.
- Coherence and Cohesion：fails to communicate any message.
- Lexical Resource：can only use a few isolated words.
- Grammatical Range and Accuracy：cannot use sentence forms at all.

### Band 0
does not attend / does not attempt the task in any way / writes a totally memorised response（所有四项）。

## 本系统评分映射

- `src/official_rubrics.py`的`IELTS`量表（Task 2）要求LLM输出`task_response`/
  `coherence_cohesion`/`lexical_resource`/`grammar_accuracy`四个0-9整数键，
  对应上面Task 2表格的四列。
- `IELTS_TASK1`量表要求输出`task_achievement`/`coherence_cohesion`/
  `lexical_resource`/`grammar_accuracy`，对应上面Task 1表格的四列。Task 1
  额外要求：至少150词、必须包含总体趋势概述（overview）、不需要也不应该给出
  个人观点或建议——这些是Task Achievement维度里"fully satisfies all the
  requirements"的具体判断依据。
- 两套量表都按四项等权平均、四舍五入到最近0.5，得到`primary_score`（0-9
  Band），对应`normalize_rubric_result()`里的计算逻辑。
