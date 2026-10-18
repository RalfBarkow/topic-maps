(in-package #:topic-maps.tmdm)

(defun same-role-signature-p (a b)
  (and (eq (%association-role-type a) (%association-role-type b))
       (eq (%association-role-player a) (%association-role-player b))))

(defun normalize-roles (association)
  ;; TMDM 5.8/6.7: shared parent; identifiers are metadata, not equality keys.
  (loop for pair = (equal-pair (%association-roles association) #'same-role-signature-p)
        while pair do
          (let* ((a (first pair)) (b (second pair))
                 (c (%make-association-role association (%association-role-type a) (%association-role-player a))))
            (setf (%association-role-item-identifiers c)
                  (set-union (%association-role-item-identifiers a) (%association-role-item-identifiers b) #'string=)
                  (%association-roles association) (replace-pair (%association-roles association) a b c)
                  (%association-role-forward a) c (%association-role-forward b) c))))

(defun equal-associations-p (a b)
  ;; TMDM 5.7: compare role sets structurally, independent of role ordering.
  ;; Role parents are the associations being compared (the equality cycle).
  ;; Scope sets are significant; identifiers do not participate in equality.
  (and (eq (%association-type a) (%association-type b))
       (same-scope-p (%association-scope a) (%association-scope b))
       (= (length (%association-roles a)) (length (%association-roles b)))
       (every (lambda (role) (find role (%association-roles b) :test #'same-role-signature-p))
              (%association-roles a))))

(defun merge-two-associations (map a b)
  ;; TMDM 6.6/6.7: retarget both equal role sets to C, then merge corresponding
  ;; Roles. This preserves their identifiers AND every retained role handle.
  (let ((c (%make-association map (%association-type a))))
    (setf (%association-scope c) (copy-list (%association-scope a))
          (%association-item-identifiers c)
          (set-union (%association-item-identifiers a) (%association-item-identifiers b) #'string=)
          (%association-roles c) (set-union (%association-roles a) (%association-roles b) #'eq)
          (%topic-map-associations map) (replace-pair (%topic-map-associations map) a b c)
          (%association-forward a) c (%association-forward b) c)
    (dolist (role (%association-roles c)) (setf (%association-role-parent role) c))
    (normalize-roles c)
    c))

(defun normalize-associations (map)
  (dolist (association (%topic-map-associations map)) (normalize-roles association))
  (loop for pair = (equal-pair (%topic-map-associations map) #'equal-associations-p)
        while pair do (merge-two-associations map (first pair) (second pair)))
  map)

(defun make-association (map type roles &key scope)
  "Create a same-map Association with a Scope Topic set. ROLES is a nonempty list of (TYPE PLAYER).
All references are validated before mutation and resolved to live Topics.
Return its current representative after duplicate normalization."
  (check-type map topic-map)
  (let ((type (live-topic type)) (scope (canonical-scope map scope)))
    (unless (eq map (%topic-parent type)) (error "Association type belongs to another map."))
    (unless (and (proper-list-p roles) roles) (error "An Association requires at least one Role."))
    (let ((references
            (mapcar (lambda (pair)
                      (unless (and (proper-list-p pair) (= 2 (length pair)))
                        (error "Each Role requires a type and a player."))
                      (let ((type (live-topic (first pair))) (player (live-topic (second pair))))
                        (unless (and (eq map (%topic-parent type)) (eq map (%topic-parent player)))
                          (error "Role type and player must belong to the Association's map."))
                        (list type player))) roles)))
      (let ((association (%make-association map type)))
        (setf (%association-scope association) scope
              (%association-roles association)
              (mapcar (lambda (pair) (%make-association-role association (first pair) (second pair))) references)
              (%topic-map-associations map) (append (%topic-map-associations map) (list association)))
        (normalize-associations map)
        (canonical-association association)))))
