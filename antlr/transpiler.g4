grammar transpiler;

/* 程序结构 */
program
    : (includeStmt)*
      (classDecl
      | interfaceDecl
      | functionDecl
      | varDecl
      | constDecl)* EOF
    ;

includeStmt
    : INCULDE literal SEMI?             // 包含库文件，如：include "minecraft_utils.mcdl";
    ;

/* 2. 注解系统 */

annotation
    : '@' ID     // 仅允许使用预定义注解
    ;

/* 3. 类系统 */
classDecl
    : annotation* CLASS ID
      (EXTENDS type)?                      // 单继承
      (IMPLEMENTS type)?               // 单接口实现
      LBRACE // 构造函数为__init__
        (varDecl
        | constDecl
        | methodDecl 
        )*

      RBRACE
    ;

interfaceDecl
    : annotation* INTERFACE ID
      (EXTENDS type)?                  // 接口单继承
      LBRACE 
        (methodDecl)*
      RBRACE
    ;



/* 4. 类型系统(阉割版) */
type
    : ID
    //| primitiveType
    ;

typeList
    :type (',' type)*
    ;
/*
primitiveType
    : TYPE_INT     // 32位整型
    | TYPE_STRING  // 字符串类型
    | TYPE_BOOLEAN // 布尔类型
    | TYPE_VOID    // 无返回值类型
    ;
*/

functionDecl
    : annotation* FUNC ID
      ( paramList)
      ((':'|'->') type)       // 返回类型标注
      block
    | annotation* FUNC type ID
      ( paramList)
      block
    ;


methodDecl
    : annotation* METHOD ID paramList (':'|'->') type block
    | annotation* METHOD type ID paramList block
    ;

paramList
    : LPAREN (paramDecl (',' paramDecl)*)? RPAREN
    | '()'
    ;

paramDecl
    : ID (':' type)   // 强制类型标注
    | type ID
    ;


block
    : LBRACE statement* RBRACE              // 代码块，包含多个语句
    | SEMI // 空的代码块
    ;


/* 6. 流程控制 */
statement
    : varDecl                               // 变量声明
    | constDecl                             // 常量声明
    | forStmt                               // for循环
    | whileStmt                             // while循环
    | assignment SEMI?                        // 赋值
    | expr SEMI?                              // 表达式语句
    | returnStmt SEMI?                        // 返回
    | block                                 // 代码块
    | ifStmt                                // 条件语句
    | breakStmt SEMI?                        // break语句
    | continueStmt SEMI?                     // continue语句
    | functionDecl                         // 函数定义
    ;

breakStmt
    : BREAK
    ;

continueStmt
    : CONTINUE
    ;

forStmt
    : FOR LPAREN forControl RPAREN block        // 传统for循环
    | FOR LPAREN type ID ':' expr RPAREN block       // 增强for循环 (expr需为可迭代class)
    ;


forControl
    : forLoopVarDecl? SEMI expr? SEMI (assignment)?
    ;


whileStmt
    : WHILE LPAREN expr RPAREN block            // while循环
    ;

constDecl
    : 'const' ID (':' type) ('=' expr) SEMI?  // 常量声明
    | 'const' type ID ('=' expr) SEMI?
    ;

// 公共规则
varDeclaration
    : ID (':' type) ('?')? ('=' expr)?
    | type ID ('?')? ('=' expr)? // 更符合大多数人习惯的变量声明
    ;

// 变量声明（带分号）
varDecl
    : VAR varDeclaration SEMI?
    | varDeclaration SEMI?
    ;

// for 循环变量声明（无分号）
forLoopVarDecl
    : VAR varDeclaration
    | varDeclaration
    ;

assignment
    : ID '=' expr                     // 变量赋值，如：count = 10
    // | expr '.' ID '=' expr 暂不实现
    ;

returnStmt
    : RETURN expr?                  // 返回语句，如：return result;
    ;

ifStmt
    : IF LPAREN expr RPAREN block (ELSE block)?  // 条件语句,expr必须是CompareExpr
    ;


/* 表达式系统 */
expr
    :
    //| lambdaExpr                            # LambdaExpression   // Lambda
    //| methodReference                       # MethodRefExpr      // 方法引用
    //| <assoc=right> expr '!'                # NotNullAssertion   // 非空断言
    //| expr '?' '.' ID                       # SafeNavigation     // 安全导航
     expr '.' ID argumentList         # MethodCall         // 方法调用
    | expr '.' ID                           # MemberAccess       // 成员访问
    //| expr '[' expr ']'                     # ArrayAccess        // 数组访问
    //| expr argumentList                # FunctionCall       // 函数调用
    | ID argumentList                  # DirectFuncCall     // 直接调用
    | primary                               # PrimaryExpr        // 基础表达式
    | '-' expr                              # NegExpr            // 负号
    | '!' expr                         #LogicalNotExpr             // not运算符
    | expr (MUL|DIV|MOD) expr                   # FactorExpr         // 算术运算
    | expr (ADD|SUB) expr                   # TermExpr
    | expr ('>' | '<' | '==' | '!=' | '<=' | '>=') expr # CompareExpr      // 比较运算
    | expr AND expr                   #LogicalAndExpr             // and运算符
    | expr OR expr                   #LogicalOrExpr              // or运算符
    ;


primary
    :ID                                    # VarExpr            // 变量
    | literal                               # LiteralExpr        // 字面量
    | LPAREN expr RPAREN                          # ParenExpr          // 括号
    | NEW ID argumentList                 # NewObjectExpr      // 显式对象创建
    //| LPAREN type RPAREN expr                     #TypeCastExpr        // 强制类型转换
    ;


/* 辅助规则 */

argumentList
    : LPAREN exprList? RPAREN
    | '()'
    ;

exprList
    : expr (',' expr)*                      // 表达式列表
    ;

literal
    : NUMBER                                // 数字
    | STRING                                // 普通字符串
    | FSTRING                               // 插值字符串
    | TRUE | FALSE                      // 布尔值
    | NULL                                // 空值
    ;

// 词法规则
/*
TYPE_INT     : 'int';
TYPE_STRING  : 'string';
TYPE_BOOLEAN : 'boolean';
TYPE_VOID    : 'void';
*/
// 分隔符（定义在ID之前）
LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
SEMI : ';';
COMMA : ',';

// 关键字（定义在ID之前）
INCULDE: 'include';
FUNC: 'func';
METHOD: 'method';
CLASS: 'class';
INTERFACE: 'interface';
EXTENDS: 'extends';
IMPLEMENTS: 'implements';
VAR: 'var';
RETURN: 'return';
FOR: 'for';
WHILE: 'while';
IF: 'if';
ELSE: 'else';
NEW: 'new';
TRUE: 'true';
FALSE: 'false';
NULL: 'null';
IN: 'in';
BREAK: 'break';
CONTINUE: 'continue';
CMD: 'cmd'
   | 'command'
   ;
ARROW: '->';
DOUBLE_COLON: '::';

// 运算符
NOT : '!';
MUL : '*';
DIV : '/';
MOD : '%';
ADD : '+';
SUB : '-';
GT  : '>';
LT  : '<';
EQ  : '==';
NEQ : '!=';
AND : '&&'
    | 'and'
    ;
OR  : '||'
    | 'or'
    ;
ASSIGN : '=';


// 数字
NUMBER: [0-9]+ ('.' [0-9]+)?;

// 字符串
STRING: '"' ( ESC | SAFE_CHAR )* '"';
FSTRING: 'f"' ( '\\' [\\"] | ~["\\$] | '${' )* '"' ; // 合并处理插值

// 转义字符（修正版）
fragment ESC: '\\' [btnfr"\\$];  // 正确转义字符集
fragment SAFE_CHAR: ~["\\\r\n];  // 安全字符

// 最后定义ID
ID  : [a-zA-Z_] [a-zA-Z0-9_]*;



// 空白处理
WS  : [ \t\r\n]+ -> skip;
LINE_COMMENT: ('//' ~[\r\n]*) -> skip;
LINE_COMMENT2: ('#' ~[\r\n]*) -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
