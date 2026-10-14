#include "AI/TenFeEnemy.h"

#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/TenFeStatsComponent.h"
#include "Components/TextRenderComponent.h"
#include "Engine/DamageEvents.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "TenFe.h"
#include "TimerManager.h"
#include "UObject/ConstructorHelpers.h"

ATenFeEnemy::ATenFeEnemy()
{
    PrimaryActorTick.bCanEverTick = true;

    GetCapsuleComponent()->InitCapsuleSize(46.0f, 96.0f);
    GetCharacterMovement()->bRunPhysicsWithNoController = true;
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 360.0f, 0.0f);
    GetCharacterMovement()->MaxWalkSpeed = 255.0f;
    GetCharacterMovement()->BrakingDecelerationWalking = 900.0f;

    BodyVisual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BodyVisual"));
    BodyVisual->SetupAttachment(RootComponent);
    BodyVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    BodyVisual->SetRelativeLocation(FVector(0.0f, 0.0f, -10.0f));
    BodyVisual->SetRelativeScale3D(FVector(0.62f, 0.62f, 1.45f));

    WeaponVisual = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WeaponVisual"));
    WeaponVisual->SetupAttachment(RootComponent);
    WeaponVisual->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    WeaponVisual->SetRelativeLocation(FVector(24.0f, 48.0f, 12.0f));
    WeaponVisual->SetRelativeRotation(FRotator(0.0f, 0.0f, 90.0f));
    WeaponVisual->SetRelativeScale3D(FVector(0.1f, 0.1f, 1.05f));

    static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderAsset(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeAsset(TEXT("/Engine/BasicShapes/Cube.Cube"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> PaladinAsset(TEXT("/Game/Characters/Enemies/Paladin/SM_PaladinSoldier_Meshy.SM_PaladinSoldier_Meshy"));
    static ConstructorHelpers::FObjectFinder<UStaticMesh> PaladinWeaponAsset(TEXT("/Game/Characters/Enemies/Paladin/SM_PaladinGreatsword.SM_PaladinGreatsword"));
    if (PaladinAsset.Succeeded())
    {
        BodyVisual->SetStaticMesh(PaladinAsset.Object);
        BodyVisual->SetRelativeLocation(FVector(0.0f, 0.0f, -99.5f));
        BodyVisual->SetRelativeRotation(FRotator::ZeroRotator);
        BodyVisual->SetRelativeScale3D(FVector::OneVector);
    }
    else if (CylinderAsset.Succeeded())
    {
        BodyVisual->SetStaticMesh(CylinderAsset.Object);
    }
    if (PaladinWeaponAsset.Succeeded())
    {
        WeaponVisual->SetStaticMesh(PaladinWeaponAsset.Object);
        WeaponVisual->SetRelativeLocation(FVector(0.0f, 59.0f, 4.0f));
        WeaponVisual->SetRelativeRotation(FRotator::ZeroRotator);
        WeaponVisual->SetRelativeScale3D(FVector::OneVector);
        WeaponVisual->SetVisibility(true);
    }
    else if (CubeAsset.Succeeded())
    {
        WeaponVisual->SetStaticMesh(CubeAsset.Object);
    }

    StatusLabel = CreateDefaultSubobject<UTextRenderComponent>(TEXT("StatusLabel"));
    StatusLabel->SetupAttachment(RootComponent);
    StatusLabel->SetRelativeLocation(FVector(0.0f, 0.0f, 145.0f));
    StatusLabel->SetHorizontalAlignment(EHorizTextAligment::EHTA_Center);
    StatusLabel->SetVerticalAlignment(EVerticalTextAligment::EVRTA_TextCenter);
    StatusLabel->SetWorldSize(24.0f);
    StatusLabel->SetTextRenderColor(FColor(225, 70, 55));

    Stats = CreateDefaultSubobject<UTenFeStatsComponent>(TEXT("Stats"));
    Stats->MaxHealth = 120.0f;
    Stats->CurrentHealth = 120.0f;
    Stats->MaxStamina = 1.0f;
    Stats->CurrentStamina = 1.0f;
    Stats->StaminaRegenerationPerSecond = 0.0f;
}

void ATenFeEnemy::BeginPlay()
{
    Super::BeginPlay();
    SpawnTransform = GetActorTransform();
    Stats->OnDeath.AddDynamic(this, &ATenFeEnemy::HandleDeath);
    AcquireTarget();
    UpdateStatusLabel(TEXT("EN ESPERA"));
}

void ATenFeEnemy::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bDead)
    {
        return;
    }

    if (!IsValid(TargetCharacter))
    {
        AcquireTarget();
    }

    FaceStatusLabelToPlayer();
    if (!IsValid(TargetCharacter))
    {
        UpdateStatusLabel(TEXT("SIN OBJETIVO"));
        return;
    }

    const float Distance = FVector::Dist2D(GetActorLocation(), TargetCharacter->GetActorLocation());
    if (Distance > DetectionRange)
    {
        UpdateStatusLabel(TEXT("EN ESPERA"));
        return;
    }

    if (Distance > AttackRange)
    {
        if (!bWindingUp)
        {
            ChaseTarget();
            UpdateStatusLabel(TEXT("PERSIGUIENDO"));
        }
        return;
    }

    GetCharacterMovement()->StopMovementImmediately();
    if (bCanAttack && !bWindingUp)
    {
        BeginAttack();
    }
}

float ATenFeEnemy::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
    Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
    if (bDead)
    {
        return 0.0f;
    }

    if (ACharacter* AttackingCharacter = Cast<ACharacter>(DamageCauser))
    {
        TargetCharacter = AttackingCharacter;
    }

    const float AppliedDamage = Stats->ApplyDamage(DamageAmount, 2.0f);
    if (!bDead)
    {
        UpdateStatusLabel(TEXT("HERIDO"));
    }
    return AppliedDamage;
}

void ATenFeEnemy::AcquireTarget()
{
    TargetCharacter = UGameplayStatics::GetPlayerCharacter(this, 0);
}

void ATenFeEnemy::ChaseTarget()
{
    if (!TargetCharacter)
    {
        return;
    }

    FVector Direction = TargetCharacter->GetActorLocation() - GetActorLocation();
    Direction.Z = 0.0f;
    Direction.Normalize();
    AddMovementInput(Direction, 1.0f);
}

void ATenFeEnemy::BeginAttack()
{
    bCanAttack = false;
    bWindingUp = true;
    WeaponVisual->SetRelativeRotation(FRotator(-35.0f, 0.0f, 45.0f));
    UpdateStatusLabel(TEXT("¡ATAQUE!"));
    GetWorldTimerManager().SetTimer(AttackWindupHandle, this, &ATenFeEnemy::ResolveAttack, AttackWindup, false);
}

void ATenFeEnemy::ResolveAttack()
{
    bWindingUp = false;
    WeaponVisual->SetRelativeRotation(FRotator::ZeroRotator);

    if (IsValid(TargetCharacter))
    {
        const float Distance = FVector::Dist2D(GetActorLocation(), TargetCharacter->GetActorLocation());
        if (Distance <= AttackRange + 35.0f)
        {
            FHitResult VisibilityHit;
            FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(TenFeEnemyAttack), false, this);
            const bool bBlocked = GetWorld()->LineTraceSingleByChannel(
                VisibilityHit,
                GetActorLocation() + FVector(0.0f, 0.0f, 55.0f),
                TargetCharacter->GetActorLocation() + FVector(0.0f, 0.0f, 55.0f),
                ECC_Visibility,
                QueryParams);

            if (!bBlocked || VisibilityHit.GetActor() == TargetCharacter)
            {
                UGameplayStatics::ApplyDamage(TargetCharacter, AttackDamage, nullptr, this, UDamageType::StaticClass());
            }
        }
    }

    UpdateStatusLabel(TEXT("RECUPERANDO"));
    GetWorldTimerManager().SetTimer(AttackRecoveryHandle, this, &ATenFeEnemy::FinishAttackRecovery, AttackCooldown, false);
}

void ATenFeEnemy::FinishAttackRecovery()
{
    bCanAttack = true;
    UpdateStatusLabel(TEXT("ALERTA"));
}

void ATenFeEnemy::HandleDeath()
{
    bDead = true;
    bCanAttack = false;
    bWindingUp = false;
    GetWorldTimerManager().ClearTimer(AttackWindupHandle);
    GetWorldTimerManager().ClearTimer(AttackRecoveryHandle);
    GetCharacterMovement()->StopMovementImmediately();
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
    SetActorHiddenInGame(true);
    UE_LOG(LogTenFe, Display, TEXT("Guardián Caído derrotado. Reaparece en 4 segundos."));
    GetWorldTimerManager().SetTimer(RespawnHandle, this, &ATenFeEnemy::RespawnEnemy, 4.0f, false);
}

void ATenFeEnemy::RespawnEnemy()
{
    SetActorTransform(SpawnTransform, false, nullptr, ETeleportType::TeleportPhysics);
    Stats->RestoreToFull();
    GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
    SetActorHiddenInGame(false);
    bDead = false;
    bCanAttack = true;
    bWindingUp = false;
    AcquireTarget();
    UpdateStatusLabel(TEXT("EN ESPERA"));
}

void ATenFeEnemy::UpdateStatusLabel(const FString& StateLabel)
{
    if (StatusLabel)
    {
        StatusLabel->SetText(FText::FromString(FString::Printf(
            TEXT("GUARDIÁN CAÍDO\n%.0f / %.0f PV\n%s"),
            Stats->CurrentHealth,
            Stats->MaxHealth,
            *StateLabel)));
    }
}

void ATenFeEnemy::FaceStatusLabelToPlayer() const
{
    if (!StatusLabel || !TargetCharacter)
    {
        return;
    }

    const FVector ToPlayer = TargetCharacter->GetActorLocation() - StatusLabel->GetComponentLocation();
    StatusLabel->SetWorldRotation(FRotator(0.0f, ToPlayer.Rotation().Yaw + 180.0f, 0.0f));
}
