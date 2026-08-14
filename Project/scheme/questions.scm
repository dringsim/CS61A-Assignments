(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))

;; Problem 15
;; Returns a list of two-element lists
(define (enumerate s)
  ; BEGIN PROBLEM 15
    (if (null? s) '()
      ;((lambda (f) (f f s 0)) (lambda (f in n) (if (= n (length s)) '() (cons (list n (car in)) (f f (cdr in) (+ n 1))))))
      (((lambda (f) (f f)) (lambda (f) (lambda (in n) (if (= n (length s)) '() (cons (list n (car in)) ((f f) (cdr in) (+ n 1))))))) s 0)
    )
  )
  ; END PROBLEM 15

;; Problem 16

;; Merge two lists S1 and S2 according to ORDERED? and return
;; the merged lists.
(define (merge ordered? s1 s2)
  ; BEGIN PROBLEM 16
  (if (null? s1) s2 (if (null? s2) s1 (if (ordered? (car s1) (car s2)) (cons (car s1) (cons (car s2) (merge ordered? (cdr s1) (cdr s2)))) (cons (car s2) (cons (car s1) (merge ordered? (cdr s1) (cdr s2)))))))
  )
  ; END PROBLEM 16

;; Optional Problem 2

;; Returns a function that checks if an expression is the special form FORM
(define (check-special form)
  (lambda (expr) (equal? form (car expr))))

(define lambda? (check-special 'lambda))
(define define? (check-special 'define))
(define quoted? (check-special 'quote))
(define let?    (check-special 'let))

;; Converts all let special forms in EXPR into equivalent forms using lambda
(define (let-to-lambda expr)
  (cond ((atom? expr)
         ; BEGIN OPTIONAL PROBLEM 2
         expr
         ; END OPTIONAL PROBLEM 2
         )
        ((quoted? expr)
         ; BEGIN OPTIONAL PROBLEM 2
         expr
         ; END OPTIONAL PROBLEM 2
         )
        ((or (lambda? expr)
             (define? expr))
         (let ((form   (car expr))
               (params (cadr expr))
               (body   (cddr expr)))
           ; BEGIN OPTIONAL PROBLEM 2
           ;`(,form ,params ,@(map let-to-lambda body))
           (cons form (cons params (map let-to-lambda body)))
           ; END OPTIONAL PROBLEM 2
           ))
        ((let? expr)
         (let ((values (cadr expr))
               (body   (cddr expr)))
           ; BEGIN OPTIONAL PROBLEM 2
           ;`((lambda ,(car (zip values)) ,@(map let-to-lambda body)) ,@(map let-to-lambda (cadr (zip values))))
           (cons (cons 'lambda (cons (car (zip values)) (map let-to-lambda body))) (map let-to-lambda (cadr (zip values))))
           ; END OPTIONAL PROBLEM 2
           ))
        (else
         ; BEGIN OPTIONAL PROBLEM 2
         (map let-to-lambda expr)
         ; END OPTIONAL PROBLEM 2
         )))

; Some utility functions that you may find useful to implement for let-to-lambda

(define (zip pairs)
  (if (null? pairs) '(() ()) (if (null? (car pairs)) nil (cons (map car pairs) (zip (map cdr pairs))))))
